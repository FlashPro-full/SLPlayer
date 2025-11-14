//--------------------------------------------------------------------------------------
// File: default.fx
//
// Copyright (c) Microsoft Corporation. All rights reserved.
//--------------------------------------------------------------------------------------

#include "InputLayout.fx"


//--------------------------------------------------------------------------------------
// 炫彩
//--------------------------------------------------------------------------------------
float4 GetDazzleColor(float2 inputPos, float4 texColor)
{
    if (texColor.a > 0) {
        float progress = 1.0f;
        if (Speed != 0) {
            progress = (NowTime - Base.beginTime) / 1000.0f * Speed;
            progress = frac(progress);
        }
        
        float2 pos = (inputPos.xy - AreaPos.xy * Scale + ScrollPoint.xy) / Scale;
        float angle = 0.0f;
        int dazzle = abs(Dazzle);

        if (1 == dazzle) { //水平拉伸渐变
            angle = frac(pos.x / AreaSize.x) * 360.0f;
        } else if (2 == dazzle) { //垂直拉伸渐变
            angle = frac(pos.y / AreaSize.y) * 360.0f;
        } else if (3 == dazzle) { //水平平铺渐变
            angle = frac(pos.x / 360.0f) * 360.0f;
        } else if (4 == dazzle) { //垂直平铺渐变
            angle = frac(pos.y / 360.0f) * 360.0f;
        } else if (5 == dazzle) { //拉伸渐变(左上角)
            angle = frac((pos.x + pos.y) / (AreaSize.x + AreaSize.y)) * 360.0f;
        } else if (6 == dazzle) { //拉伸渐变(左下角)
            angle = frac((pos.x + AreaSize.y - pos.y) / (AreaSize.x + AreaSize.y)) * 360.0f;
        } else if (7 == dazzle) { //平铺渐变(左上角)
            angle = frac((pos.x + pos.y) / (360.0f)) * 360.0f;
        } else if (8 == dazzle) { //平铺渐变(左下角)
            angle = frac((pos.x + AreaSize.y - pos.y) / (360.0f)) * 360.0f;
        } else if (9 == dazzle) { //旋转渐变
            float x = (pos.x * 2.0f - AreaSize.x) / AreaSize.x;
            float y = (pos.y * 2.0f - AreaSize.y) / AreaSize.y;
            float radians = atan2(x, y);
            angle = degrees(radians);
            if (angle < 0.0f) {
                angle += 360.0f;
            }
        }
        
        angle = frac((angle + progress * 360.0f) / 360.0f) * 360.0f;    
        texColor = HSV2RGB(float4(angle, 1.0f, 1.0f, texColor.a));
    }
    
    return texColor; 
}


//--------------------------------------------------------------------------------------
// 顶点着色器
//--------------------------------------------------------------------------------------
PS_INPUT VSDefault( VS_INPUT input )
{
    PS_INPUT output = (PS_INPUT)0;
    output.Pos = input.Pos;
    output.Tex = input.Tex;
    return output;
}


//--------------------------------------------------------------------------------------
// 像素着色器（纹理）
//--------------------------------------------------------------------------------------
float4 PSDefault( PS_INPUT input) : SV_Target
{
    float4 color = txDiffuse.Sample( samLinear, input.Tex);

    // 裁剪掉透明的像素
    clip(color.a - 0.01f);

    return color;
}


float4 PSLine(PS_INPUT input)  : SV_Target
{
    return float4(1.0f, 1.0f, 1.0f, 1.0f);
}


float4 PSSelectedLine(PS_INPUT input)  : SV_Target
{
    return float4(0.0f, 0.0f, 1.0f, 1.0f);
}


//--------------------------------------------------------------------------------------
// 顶点着色器
//--------------------------------------------------------------------------------------
PS_INPUT VS(VS_INPUT input)
{
    return DefaultVS(input);
}


//--------------------------------------------------------------------------------------
// 像素着色器（纹理）
//--------------------------------------------------------------------------------------
float4 PS( PS_INPUT input) : SV_Target
{
        float4 color = DefaultPS(input);
    if(Base.renderMode == 1){
        //color = AdjustmentPS(input, color);
    } else if(Base.renderMode == 2){
        return color;
    } else if (Base.renderMode == 3) {
        color = GetDazzleColor(input.Pos.xy, color);
    } 

    return AdjustmentPS(input, color);
}


//--------------------------------------------------------------------------------------
// 像素着色器（纹理）
//--------------------------------------------------------------------------------------
float4 PS_9( PS_INPUT input) : SV_Target
{
        float4 color = DefaultPS(input);
    if(Base.renderMode == 1){
        // color = AdjustmentPS(input, color);
    } else if(Base.renderMode == 2){
        return color;
    } else if (Base.renderMode == 3) {
        color = GetDazzleColor(float2(input.Tex.x * TexSize.x, input.Tex.y * TexSize.y), color);
    } 

    return AdjustmentPS(input, color);
}