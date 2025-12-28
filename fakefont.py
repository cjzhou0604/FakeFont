import os
import random
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

def create_fake_font(original_font_path, output_font_path, seed=42):
    """
    读取原始 .ttc 或 .ttf 字体，打乱 cmap 映射，生成混淆字体。
    返回：编码映射字典 {original_unicode: new_unicode}
    """
    random.seed(seed)  # 确保可复现

    # 加载字体（如果是 .ttc，取第一个字体）
    font = TTFont(original_font_path, fontNumber=0)

    # 获取所有 cmap 子表（通常有多个平台）
    cmap_tables = font['cmap'].tables
    # 找到 Unicode 平台的 cmap（platformID=0 或 3, platEncID=1 或 10）
    unicode_cmap = None
    for table in cmap_tables:
        if table.platformID == 3 and table.platEncID in (1, 10):  # Windows Unicode
            unicode_cmap = table
            break
    if unicode_cmap is None:
        for table in cmap_tables:
            if table.platformID == 0:  # Unicode platform
                unicode_cmap = table
                break
    if unicode_cmap is None:
        raise ValueError("未找到 Unicode cmap 表")

    # 获取所有有效的 Unicode -> glyphID 映射
    original_mapping = unicode_cmap.cmap  # dict: unicode_int -> glyph_name
    unicode_chars = list(original_mapping.keys())
    glyph_names = list(original_mapping.values())

    if len(unicode_chars) != len(set(glyph_names)):
        print("警告：存在多对一字形（ligature 或重复映射），可能影响效果")

    # 随机打乱 Unicode 编码列表（保持字形顺序不变，重分配编码）
    shuffled_chars = unicode_chars[:]
    random.shuffle(shuffled_chars)

    # 构建新映射：shuffled_chars[i] -> glyph_names[i]
    new_cmap_dict = {}
    for char, glyph in zip(shuffled_chars, glyph_names):
        new_cmap_dict[char] = glyph

    # 创建新的 cmap 子表
    new_cmap = CmapSubtable.newSubtable(unicode_cmap.format)
    new_cmap.platformID = unicode_cmap.platformID
    new_cmap.platEncID = unicode_cmap.platEncID
    new_cmap.language = unicode_cmap.language
    new_cmap.cmap = new_cmap_dict

    # 替换原 cmap 表中的子表
    for i, table in enumerate(cmap_tables):
        if table is unicode_cmap:
            font['cmap'].tables[i] = new_cmap
            break

    # 构建反向映射：原字符 -> 新字符（用于后续文本转换）
    # 注意：因为是打乱的，所以 old_char -> new_char 满足：
    #   old_char 对应 glyph G
    #   new_char 也对应 glyph G（在新字体中）
    # 所以：在新字体中显示 new_char，看起来像 old_char
    reverse_map = {}
    glyph_to_old_char = {g: c for c, g in original_mapping.items()}
    glyph_to_new_char = {g: c for c, g in new_cmap_dict.items()}

    for glyph in glyph_to_old_char:
        if glyph in glyph_to_new_char:
            old_char = glyph_to_old_char[glyph]
            new_char = glyph_to_new_char[glyph]
            reverse_map[old_char] = new_char

    # 保存新字体
    font.save(output_font_path)
    font.close()

    return reverse_map


def encode_text_with_fake_font(text, reverse_map):
    """
    将原文本转换为“在新字体下显示相同字形”的文本。
    即：每个字符 c → reverse_map.get(c, c)
    """
    return ''.join(reverse_map.get(ord(c), ord(c)) if isinstance(c, str) else c for c in text)


# ======================
# 主程序
# ======================
if __name__ == "__main__":
    import sys

    # 输入原始字体
    original_font = "simsun.ttc"
    fake_font = "fakesimsun.ttc"

    if not os.path.exists(original_font):
        print(f"错误：找不到字体文件 {original_font}")
        sys.exit(1)

    print("正在生成混淆字体...")
    reverse_mapping = create_fake_font(original_font, fake_font, seed=12345)
    print(f"✅ 已生成混淆字体: {fake_font}")
    print(f"共混淆 {len(reverse_mapping)} 个字符")

    # 示例：用户输入一段话
    sample_text = input("\n请输入一段中文文本（使用原字体显示正确的内容）:\n")
    
    # 转换为“新字体下显示相同字形”的文本
    encoded_text = ''.join(
        chr(reverse_mapping.get(ord(c), ord(c))) if ord(c) in reverse_mapping else c
        for c in sample_text
    )

    print("\n📄 在 fakesimsun.ttc 字体下，以下文本将显示为你输入的内容：")
    print(repr(encoded_text))
    print("\n👀 实际显示（请用新字体查看）:")
    print(encoded_text)

    # 可选：保存映射表供后续使用
    with open("char_mapping.txt", "w", encoding="utf-8") as f:
        for old_code, new_code in sorted(reverse_mapping.items()):
            f.write(f"{old_code:04X} -> {new_code:04X} : {chr(old_code)} -> {chr(new_code)}\n")
    print("\n💾 字符映射已保存到 char_mapping.txt")
