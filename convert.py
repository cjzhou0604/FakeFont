# gen_js_map.py
forward_lines = []
reverse_dict = {}  # 用于自动去重：new_code -> old_code

try:
    with open("char_mapping.txt", "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or "->" not in line or ":" not in line:
                continue
            try:
                # 提取冒号前的部分（如 "0020 -> 8359"）
                cmap_part = line.split(":", 1)[0].strip()
                if "->" not in cmap_part:
                    continue
                old_hex, new_hex = cmap_part.split("->", 1)
                old_hex = old_hex.strip()
                new_hex = new_hex.strip()

                # 验证是否为合法十六进制字符串
                if not all(c in "0123456789ABCDEFabcdef" for c in old_hex):
                    continue
                if not all(c in "0123456789ABCDEFabcdef" for c in new_hex):
                    continue

                old_code = int(old_hex, 16)
                new_code = int(new_hex, 16)

                forward_lines.append(f"    {old_code}: {new_code}")
                reverse_dict[new_code] = old_code  # 自动覆盖重复项

            except Exception as e:
                print(f"⚠️ 第 {line_num} 行解析失败: {line!r} | 错误: {e}")

    # 构建正向和反向 JS 对象
    js_forward = "const forwardMap = {\n" + ",\n".join(forward_lines) + "\n};\n"
    reverse_lines = [f"    {new_code}: {old_code}" for new_code, old_code in sorted(reverse_dict.items())]
    js_reverse = "const reverseMap = {\n" + ",\n".join(reverse_lines) + "\n};\n"

    # 写入 mapping.js 文件
    with open("mapping.js", "w", encoding="utf-8") as out:
        out.write(js_forward)
        out.write("\n")
        out.write(js_reverse)

    print("✅ 成功生成 mapping.js 文件！")

except FileNotFoundError:
    print("❌ 错误：找不到 char_mapping.txt 文件，请确保它在当前目录。")
except Exception as e:
    print(f"❌ 发生未知错误: {e}")
