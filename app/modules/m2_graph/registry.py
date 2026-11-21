from app.keys import ReplayError, identifier


def catalog(records):
    out = {}
    for row in records:
        try:
            name = identifier(row["id"])
            revision = identifier(row["revision"])
            inputs = row["inputs"]
            if name in out or not isinstance(inputs, list) or len(inputs) > 12:
                raise ValueError("重复节点或依赖数超限")
            links = set()
            for link in inputs:
                lag = link.get("lag", 0)
                edge = (identifier(link["dataset"]), lag)
                if type(lag) is not int or not 0 <= lag <= 7 or edge in links:
                    raise ValueError("依赖时差或空边无效")
                links.add(edge)
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise ReplayError("DATASET", "数据集定义或依赖无效") from exc
        out[name] = {"revision": revision, "reads": sorted(links)}
    for node, record in out.items():
        unknown = {p for p, _ in record["reads"]} - out.keys()
        if unknown:
            raise ReplayError("MISSING_DATASET", f"{node} 缺少依赖 {sorted(unknown)[0]}")
    return out
