//--------------------------------------------------------------------------------------
// File: InputLayout.fx
//
// Copyright (c) Microsoft Corporation. All rights reserved.
//--------------------------------------------------------------------------------------

// custom struct type
struct RECT
{
    int    left;
    int    top;
    int    right;
    int    bottom;
};

struct CBITEMBASE
{
    int renderMode;         ///< 当前渲染模式（0： 纹理，1： 背景，2：线框）
    int playState;          ///< 播放状态(0:播放， 1：暂停， 2：停止，3：停止在最后一帧，4：黑屏)
    int fmt;                ///< HSFormat 类型
    float playProgress;     ///< 播放进度（只有播放状态为“暂停”和“停止在最后一帧”才有效）
    float beginTime;       ///< 起始时间，结合当前时间来确认播放进度
    float periodTime;      ///< 起始时间，播放时间周期
    bool alphaChannel;      ///< 透明通道在前(ARGB/ABGR)
    float alpha;            ///< 透明度
    float luminance;        ///< 亮度(0.0 - 1.0)
    float saturation;       ///< 饱和度
    float contrast;         ///< 对比度
    float feather;          ///< 羽化
    bool  dashedLine;       ///< 使用虚线（renderMode为2时有效）
    int fade;               ///< 淡入淡出（0：没有进入状态，1：淡入，-1：淡出）
    float fadeMicrosecond; ///< 淡入淡出时长
    float fadeMicrosecondBegin;///< 淡入淡出开始
    float4 color;           ///< 颜色
};

//--------------------------------------------------------------------------------------
// Constant Buffer Variables
//--------------------------------------------------------------------------------------
Texture2D txDiffuse : register( t0);
Texture2D txDiffuseU : register(t1);
Texture2D txDiffuseV : register(t2);
SamplerState samLinear : register( s0 );

cbuffer cbGlobal : register( b0 )
{
    int2 ScreenSize;        ///< 屏幕大小
    float2 reserved;        ///< 预留

    matrix ViewMatrix;      ///< 视图坐标转换矩阵
};

cbuffer cbItemFrame : register( b1 )
{
    CBITEMBASE Base;        ///< 基本信息（最好不作为基类，不确定内存分布）
    RECT Clip;              ///< 裁剪（顺序为左、上、右、下）
    int Mirror;             ///< 镜像， 1:水平镜像，2、垂直镜像，3、水平和垂直镜像
    int Alignment;          ///< 对齐方式（跟拉伸有关系）， 1:上，2、下、4：左、8:右
    bool DisableStretch;    ///< 禁用拉伸
    int Effect;             ///< 预留

    int2 AreaSize;          ///< 区域大小(cx, cy)
    int2 TexSize;           ///< 纹理大小(cx, cy)
    bool KeepAspectRatio;   ///< 保持比例
    int Dazzle;             ///< 特效索引
    float Speed;            ///< 速度(0:静止, >0:正向, <0:反向)
    float Reserved1;        ///< 预留
    int2 AreaPos;           ///< 区域位置
    float2 Reserved2;       ///< 预留
};

cbuffer cbGlobalFrame : register( b2 )
{
    float NowTime;          ///< 当前时间
    float Scale;            ///< 模拟屏的缩放大小（目前给炫彩使用）
    float2 ScrollPoint;     ///< 原坐标平移的位置（目前给炫彩使用）
};

struct VS_INPUT
{
    float4 Pos : POSITION;
    float2 Tex : TEXCOORD0;
};

struct PS_INPUT
{
    float4 Pos : SV_POSITION;
    float2 Tex : TEXCOORD0;
};

//--------------------------------------------------------------------------------------
// 获取播放进度
//--------------------------------------------------------------------------------------
float GetProgress()
{
    float progress = 0.0f;
    ///< 播放状态(0:播放， 1：暂停， 2：停止，3：停止在最后一帧，4：黑屏)
    if (0 == Base.playState) { //播放
        progress = (NowTime - Base.beginTime) / Base.periodTime;
    } else if (1 == Base.playState) {//暂停
        progress = Base.playProgress;
    }/* else if (2 == Base.playState) {//停止
        progress = 0;
    } */else if (3 == Base.playState) {//停止在最后一帧
        progress = Base.playProgress;
    } else if (4 == Base.playState) {//黑屏
        progress = Base.playProgress;
    }

    return progress;
}

float4 RGB2HSV(float4 rgb)
{
   float R = rgb.r;
   float G = rgb.g;
   float B = rgb.b;
   float A = rgb.a;
   float4 hsv;
   float max1 = max(R, max(G, B));
   float min1 = min(R, min(G, B));
   if (R == max1) {
       hsv.x = (G - B) / (max1 - min1);
   }

   if (G == max1) {
       hsv.x = 2.0 + (B - R) / (max1 - min1);
   }

   if (B == max1) {
       hsv.x = 4.0 + (R - G) / (max1 - min1);
   }

   hsv.x = hsv.x * 60.0;
   if (hsv.x  < 0.0){
       hsv.x = hsv.x + 360.0;
   }

   hsv.z = max1;
   hsv.y = (max1 - min1) / max1;
   hsv.w = A;
   return hsv;
}

float4 HSV2RGB(float4 hsv)
{
   float R;
   float G;
   float B;
   if (hsv.y == 0.0) {
       R = G = B = hsv.z;
   } else {
       hsv.x = hsv.x / 60.0;
       int i = int(hsv.x);
       float f = hsv.x - float(i);
       float a = hsv.z * (1.0 - hsv.y);
       float b = hsv.z * (1.0 - hsv.y * f);
       float c = hsv.z * (1.0 - hsv.y * (1.0 - f));
       if (i == 0)
      {
          R = hsv.z;
          G = c;
          B = a;
      }
       else if (i == 1)
      {
          R = b;
          G = hsv.z;
          B = a;
      }
       else if (i == 2)
      {
          R = a;
          G = hsv.z;
          B = c;
      }
       else if (i == 3)
      {
          R = a;
          G = b;
          B = hsv.z;
      }
       else if (i == 4)
      {
          R = c;
          G = a;
          B = hsv.z;
      }
      else
      {
          R = hsv.z;
          G = a;
          B = b;
      }
   }

   return float4(R, G, B, hsv.w);
}


float4 RGB2HLS(float4 rgba)
{
    float dr = rgba.r;
    float dg = rgba.g;
    float db = rgba.b;

    float cmax = max(dr, max(dg, db));
    float cmin = min(dr, min(dg, db));
    float cdes = cmax - cmin;
    float hh, ll, ss;

    ll = (cmax+cmin)/2;
    if(cdes){
        if(ll <= 0.5)
            ss = (cmax-cmin)/(cmax+cmin);
        else
            ss = (cmax-cmin)/(2-cmax-cmin);

        if(cmax == dr){
            hh = (0+(dg-db)/cdes)*60;
        } else if(cmax == dg){
            hh = (2+(db-dr)/cdes)*60;
        } else{
            hh = (4+(dr-dg)/cdes)*60;
        }

        if(hh<0){
            hh+=360;
        }
    }else {
        hh = ss = 0;
    }

    return float4(hh, ll, ss, rgba.a);
}

float HLS2RGBvalue(float n1, float n2, float hue)
{
    if(hue > 360){
        hue -= 360;
    } else if(hue < 0) {
        hue += 360;
    }

    if(hue < 60){
        return n1+(n2-n1)*hue/60;
    } else if(hue < 180){
        return n2;
    } else if(hue < 240){
        return n1+(n2-n1)*(240-hue)/60;
    }

    return n1;
}

float4 HLS2RGB(float4 hlsa)
{
    float l = hlsa.g;
    float s = hlsa.b;

    float r = 0.0f;
    float g = 0.0f;
    float b = 0.0f;
    float cmax = 0.0f;

    if(l <= 0.5){
        cmax = l*(1+s);
    } else {
        cmax = l*(1-s)+s;
    }

    float cmin = 2*l-cmax;

    if(s == 0){
        r = g = b = l;
    }else{
        r = HLS2RGBvalue(cmin, cmax, hlsa.r +120);
        g = HLS2RGBvalue(cmin, cmax, hlsa.r);
        b = HLS2RGBvalue(cmin, cmax, hlsa.r -120);
    }

    return float4(r, g, b, hlsa.a);
}

//--------------------------------------------------------------------------------------
// RGBA 亮度调节
//--------------------------------------------------------------------------------------
float4 AdjustLuminance(float4 color, float lum, float saturation)
{
    float4 hsva = RGB2HSV(color);
    hsva.b *= lum;
    hsva.g *= saturation;

    return HSV2RGB(hsva);
}


//--------------------------------------------------------------------------------------
// 从Yuv420p 获取RGBA
//--------------------------------------------------------------------------------------
float4 YUV420PS(PS_INPUT input)
{
    float y = txDiffuse.Sample(samLinear, input.Tex).r;
    float u = txDiffuseU.Sample(samLinear, input.Tex).r  - 0.5f;
    float v = txDiffuseV.Sample(samLinear, input.Tex).r  - 0.5f;
    float r = y + 1.14f * v;
    float g = y - 0.394f * u - 0.581f * v;
    float b = y + 2.03f * u;

    return float4(r,g,b, 1.0f);
}


//--------------------------------------------------------------------------------------
// 从NV12 获取RGBA
//--------------------------------------------------------------------------------------
float4 NV12PS(PS_INPUT input)
{
    float y = txDiffuse.Sample(samLinear, input.Tex).r;
    float u = txDiffuseU.Sample(samLinear, input.Tex).r  - 0.5f;
    float v = txDiffuseU.Sample(samLinear, input.Tex).g  - 0.5f;
    float r = y + 1.14f * v;
    float g = y - 0.394f * u - 0.581f * v;
    float b = y + 2.03f * u;

    return float4(r,g,b, 1.0f);
}


//--------------------------------------------------------------------------------------
// 从NV12 获取RGBA
//--------------------------------------------------------------------------------------
float4 NV21PS(PS_INPUT input)
{
    float y = txDiffuse.Sample(samLinear, input.Tex).r;
    float u = txDiffuseU.Sample(samLinear, input.Tex).g  - 0.5f;
    float v = txDiffuseU.Sample(samLinear, input.Tex).r  - 0.5f;
    float r = y + 1.14f * v;
    float g = y - 0.394f * u - 0.581f * v;
    float b = y + 2.03f * u;

    return float4(r, g, b, 1.0f);
}

//--------------------------------------------------------------------------------------
// 颜色调节
//--------------------------------------------------------------------------------------
float4 ColorAdjustment(float4 texColor, float2 tex)
{
    if(Base.contrast != 1.0f){
        // 对比度计算方式
        texColor = float4((texColor.rgb - 0.5) * max(Base.contrast, 0.0) + 0.5, texColor.a);
    }

    float lumi = Base.luminance;
    if(Base.feather != 0.0f){
        // 羽化
        float x = tex.x * 2.0f - 1.0f;
        float y = tex.y * 2.0f - 1.0f;
        lumi *= 1.0f - min(Base.feather * (x * x + y * y), 1.0f);
    }

    if(lumi != 1.0f || Base.saturation != 1.0f){
        // 亮度和饱和度
        texColor = AdjustLuminance(texColor, lumi, Base.saturation);
    }

    float fade = 1.0f;
    if(Base.fade != 0 && Base.fadeMicrosecond != 0.0){
        if(Base.fade > 0){
            fade = (NowTime - Base.fadeMicrosecondBegin) / Base.fadeMicrosecond;
        } else {
            fade = ((Base.fadeMicrosecondBegin + Base.fadeMicrosecond) - NowTime) / Base.fadeMicrosecond;
        }

        fade = clamp(fade, 0.0f , 1.0f);
    }

    if(Base.alpha != 0.0f || fade != 1.0f){
        // 透明度
        texColor.a *= max(min(1.0f - Base.alpha, fade), 0.0f);
    }

    return texColor;
}

//--------------------------------------------------------------------------------------
// 顶点着色器
//--------------------------------------------------------------------------------------
PS_INPUT DefaultVS( VS_INPUT input )
{
    //float pointX = 0.0f; // -0.5f：左，0.5f：右
    //float pointY = 0.0f; // -0.5f：上，0.5f：下

    //float2 tex = input.Tex;
    //if (Mirror == 1 || Mirror == 3) {
    //    // 水平镜像
    //    if (tex.x == 0.0f) {
    //        tex.x = 1.0f;
    //    } else {
    //        tex.x = 0.0f;
    //    }
    //}

    //if (Mirror == 2 || Mirror == 3){
    //    // 垂直镜像
    //    if(tex.y == 0.0f){
    //        tex.y = 1.0f;
    //    }else{
    //        tex.y = 0.0f;
    //    }
    //}

    //// 计算当前的坐标序号
    //if (tex.x == 0.0f) {
    //    // 左边
    //    pointX = -0.5f;
    //} else {
    //    // 右边
    //    pointX = 0.5f;
    //}

    //if (tex.y == 0.0f) {
    //    // 上边
    //    pointY = -0.5f;
    //} else {
    //    // 下边
    //    pointY = 0.5f;
    //}

    //int alignmentH = (Alignment / 4) % 4;
    //int alignmentV = Alignment % 4;

    //// 处理图片不缩放
    //if (DisableStretch) {
    //    // 计算纹理不缩放时坐标
    //    float xScale = ((float)AreaSize.x) / TexSize.x;
    //    float yScale = ((float)AreaSize.y) / TexSize.y;

    //    if(alignmentH == 1) {
    //        if (pointX > 0.0f) {
    //            // 修改右边
    //            tex.x = xScale;
    //        }
    //    } else if(alignmentH == 2) {
    //        // 右对齐
    //        if (pointX < 0.0f) {
    //            // 修改左边
    //            tex.x = 1.0f - xScale;
    //        }
    //    } else if(alignmentH == 0){
    //        tex.x = xScale * pointX + 0.5f;
    //    }

    //    if(alignmentV == 1) {
    //        if (pointY > 0.0f) {
    //            // 修改下边
    //            tex.y = yScale;
    //        }
    //    } else if(alignmentV == 2) {
    //        if (pointY < 0.0f) {
    //            // 修改上边
    //            tex.y = 1.0f - yScale;
    //        }
    //    } else if(alignmentV == 0){
    //        tex.y = yScale * pointY + 0.5f;
    //    }
    //} else if(KeepAspectRatio) {
    //    // 按比例缩放
    //    float xScale = ((float)AreaSize.x) / TexSize.x;
    //    float yScale = ((float)AreaSize.y) / TexSize.y;
    //    float scale = min(xScale, yScale);

    //    tex.x = pointX * xScale / scale + 0.5f;
    //    tex.y = pointY * yScale / scale + 0.5f;
    //}

    //// 水平方向处理裁剪
    //if(alignmentH == 3 || !DisableStretch) {
    //    if (pointX < 0.0f) {// 左边
    //        tex.x += ((float)Clip.left) / TexSize.x;
    //    } else {// 右边
    //        tex.x -= ((float)Clip.right) / TexSize.x;
    //    }
    //} else if(alignmentH == 1) {
    //    tex.x += ((float)Clip.left) / TexSize.x;
    //} else if(alignmentH == 2) {
    //    tex.x -= ((float)Clip.right) / TexSize.x;
    //} else if(alignmentH == 0) {
    //    tex.x += ((float)Clip.left * 0.5) / TexSize.x;
    //    tex.x -= ((float)Clip.right * 0.5) / TexSize.x;
    //}

    //// 垂直方向处理裁剪
    //if(alignmentV == 3 || !DisableStretch) {
    //    if (pointY < 0.0f) {// 上边
    //        tex.y += ((float)Clip.top) / TexSize.y;
    //    } else {// 下边
    //        tex.y -= ((float)Clip.bottom) / TexSize.y;
    //    }
    //} else if(alignmentV == 1) {
    //    tex.y += ((float)Clip.top) / TexSize.y;
    //} else if(alignmentV == 2) {
    //    tex.y -= ((float)Clip.bottom) / TexSize.y;
    //} else if(alignmentH == 0) {
    //    tex.y += ((float)Clip.top * 0.5) / TexSize.y;
    //    tex.y -= ((float)Clip.bottom * 0.5) / TexSize.y;
    //}

    PS_INPUT output = (PS_INPUT)0;
    output.Pos = mul(ViewMatrix, float4(input.Pos.xyz, 1.0f));//float4(input.Pos.x + OffsetPos.x , input.Pos.y + OffsetPos.y ,input.Pos.z + OffsetPos.z ,input.Pos.w + OffsetPos.w );
    output.Tex = input.Tex;

    return output;
}


//--------------------------------------------------------------------------------------
// 像素着色器（纹理）
//--------------------------------------------------------------------------------------
float4 DefaultPS(PS_INPUT input)
{
    if (Base.renderMode != 0 && Base.renderMode != 3) {
        return Base.color;
    }

    float4 texColor = float4(0.0f, 0.0f, 0.0f, 0.0f);
    if (1 == Base.fmt) {
        texColor = YUV420PS(input);
    } else if (2 == Base.fmt) {
        texColor = NV12PS(input);
    } else if (3 == Base.fmt) {
        texColor = NV21PS(input);
    } else {
        texColor = txDiffuse.Sample(samLinear, input.Tex);
        if (4 == Base.fmt) {
            texColor = texColor.bgra;
        } else if (6 == Base.fmt) {
            texColor.a = 1.0f;
            texColor = texColor.bgra;
        } else if (7 == Base.fmt) {
            texColor.a = 1.0f;
        } else if (8 == Base.fmt) {
            texColor = texColor.argb;
        } else if (9 == Base.fmt) {
            texColor = texColor.abgr;
        } else if (10 == Base.fmt) {
            texColor.b = 1.0f;
            texColor = texColor.argb;
        } else if (11 == Base.fmt) {
            texColor.r = 1.0f;
            texColor = texColor.abgr;
        }
    }

    return texColor;
}

//--------------------------------------------------------------------------------------
// 像素着色器（纹理）
//--------------------------------------------------------------------------------------
float4 AdjustmentPS( PS_INPUT input, float4 color)
{
    if((color.a - 0.01f) < 0.0f){
        return color;
    }

    return ColorAdjustment(color, input.Tex);
}

