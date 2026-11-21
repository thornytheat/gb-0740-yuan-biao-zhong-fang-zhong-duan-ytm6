from importlib import import_module

VIEWS = {
    "intake": ("来源登记", ["登记来源", "登记交付", "隔离", "重复"]),
    "mapping": ("映射证据", ["映射", "证据", "对照"]),
    "admission": ("准入总览", ["准入", "覆盖范围", "未切换"]),
    "operations": ("三务口径", ["发布", "回查", "补数"]),
    "rollback": ("回退演练", ["回退"]),
    "reconcile": ("覆盖勾稽", ["勾稽"]),
    "issue": ("准入签发", ["批次"]),
}


def register(app):
    for number, name in enumerate(VIEWS, 1):
        app.register_blueprint(import_module(f"app.modules.m{number}_{name}.handler").api)
