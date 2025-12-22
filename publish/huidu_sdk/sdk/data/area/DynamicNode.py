from typing import Optional
from sdk.data.area.TextNode import TextNode  # Import base class
from sdk.data.other.Effect import Effect  # Import dependency classes


class DynamicNode(TextNode):
    def __init__(self, *args):
        super().__init__()
        self.set_type("dynamic")  # Override type to "dynamic"

        self.keys: Optional[str] = None
        self.dataSourceDefault: Optional[str] = None
        self.dataSource: Optional[str] = None

        self.effect = Effect(Effect.EffectType.IMMEDIATE_SHOW)
        self.effect.set_hold(360000)  # 360000 ms = 6 minutes

        if len(args) == 2:
            # Text and keys constructor
            self.string = args[0]  # Text content
            self.keys = args[1]  # Keys
        elif len(args) == 1 and isinstance(args[0], DynamicNode):
            # Copy constructor
            self._copy_from(args[0])

    def _copy_from(self, other: 'DynamicNode'):
        super()._copy_from(other)  # Copy base class properties
        self.keys = other.keys
        self.dataSourceDefault = other.dataSourceDefault
        self.dataSource = other.dataSource

    # Property accessors
    def get_keys(self) -> Optional[str]:
        return self.keys

    def set_keys(self, keys: str):
        self.keys = keys

    def get_data_source(self) -> Optional[str]:
        return self.dataSource

    def set_data_source(self, data_source: str):
        self.dataSource = data_source

    def get_data_source_default(self) -> Optional[str]:
        return self.dataSourceDefault

    def set_data_source_default(self, data_source_default: str):
        self.dataSourceDefault = dataSourceDefault

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "keys": self.keys,
            "dataSourceDefault": self.dataSourceDefault,
            "dataSource": self.dataSource
        })
        return data

    def __repr__(self) -> str:
        return (f"DynamicNode(uuid={self.id}, name='{self.name}', "
                f"string='{self.string}', keys='{self.keys}')")