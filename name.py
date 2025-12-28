from fontTools.ttLib import TTFont

def rename_font(font_path, output_path, new_family_name, new_full_name=None, new_postscript_name=None):
    """
    修改字体文件的名称信息。
    
    参数:
        font_path: 原始字体路径（.ttf 或 .ttc）
        output_path: 输出新字体路径
        new_family_name: 新的字体家族名（如 "FakeSimSun"）
        new_full_name: 新的完整字体名（默认为 new_family_name + " Regular"）
        new_postscript_name: 新的 PostScript 名（默认自动转换）
    """
    # 加载字体（如果是 .ttc，加载第一个字体）
    font = TTFont(font_path, fontNumber=0)

    if new_full_name is None:
        new_full_name = new_family_name + " Regular"
    if new_postscript_name is None:
        # PostScript 名不能有空格，通常用连字符或直接拼接
        new_postscript_name = new_family_name.replace(" ", "") + "-Regular"

    # 标准 name ID 对应关系（Windows 平台，Unicode 编码）
    NAME_IDS = {
        1: new_family_name,      # Font Family
        2: "Regular",            # Font Subfamily (Style)
        3: new_full_name,        # Unique Font Identifier
        4: new_full_name,        # Full Font Name
        6: new_postscript_name,  # PostScript Name
        16: new_family_name,     # Preferred Family (for WPF etc.)
        17: "Regular",           # Preferred Subfamily
    }

    # 遍历 name 表中的所有记录
    name_table = font["name"]
    for record in name_table.names:
        # 只处理 Windows 平台（platformID=3）的 Unicode 记录（常用）
        if record.platformID == 3 and record.nameID in NAME_IDS:
            new_name = NAME_IDS[record.nameID]
            # 编码必须匹配原记录（通常是 UTF-16 BE）
            record.string = new_name.encode("utf-16-be")

    # 保存新字体
    font.save(output_path)
    font.close()
    print(f"✅ 字体已重命名并保存为: {output_path}")


# ======================
# 使用示例
# ======================
if __name__ == "__main__":
    rename_font(
        font_path="fakesimsun.ttc",
        output_path="fakesimsun.ttf",  # 注意：.ttc 改名后建议转为 .ttf（单字体）
        new_family_name="FakeSimSun",
        new_full_name="FakeSimSun Regular"
    )
