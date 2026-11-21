from importlib import import_module

VIEWS = {
    "inventory": ("分区登记", ["登记", "隔离", "重复"]),
    "graph": ("依赖求解", ["依赖"]),
    "fingerprint": ("清单指纹", ["指纹"]),
    "schedule": ("重放排程", ["排程"]),
    "rollback": ("回滚校验", ["回滚"]),
    "reconcile": ("行数勾稽", ["分区勾稽"]),
    "release": ("版本签发", ["批次"]),
}


def register(app):
    for number, name in enumerate(VIEWS, 1):
        app.register_blueprint(import_module(f"app.modules.m{number}_{name}.handler").api)
