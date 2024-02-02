from weasyprint import HTML


def generate_pdf(output_file):
    arabic_text = "مرحبا بك"
    html_content = (f"<html>"
                    f"<meta http-equiv='Content-type' content='text/html; charset=UTF-8' />"
                    f"<head><style>@page {{size: A4 landscape;direction: rtl;}}body{{direction: rtl;}}"
                    f"table{{border-collapse: collapse;}}table,tr,th,td{{border: solid 1px}}"
                    f"th{{direction: rtl;text-align:center;width:auto}}</style></head>"
                    f"<body>"
                    f"{arabic_text}"
                    f"<table>"
                    f"<tr>"
                    f"<th>تاريخ الاصدار</th><th>اليوم</th><th>حالة اليوم</th><th>الموقع</th><th>كود الماكينة</th>"
                    f"<th>استمارة فئة 125 جنيه</th><th>استمارة فئة 175 جنيه</th><th>استمارة فئة 50 جنيه</th>"
                    f"<th>اجمالى عدد المصدرات</th><th>حالة الماكينة</th><th>النسبة 125</th><th>النسبة 175</th>"
                    f"<th>النسبة 50</th><th>اجمالى النسبة</th><th>اجمالى نسبة سيتك</th>"
                    f"</tr>"
                    f"<tr>"
                    f"<td>1</td>"
                    f"<td>2</td>"
                    f"<td>3</td>"
                    f"<td>4</td>"
                    f"<td>5</td>"
                    f"<td>6</td>"
                    f"<td>7</td>"
                    f"</tr>"
                    f"</table>"
                    f"</body>"
                    f"</html>")

    # Save HTML content to a file
    with open("temp.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    # Generate PDF from HTML
    HTML(string=html_content).write_pdf(output_file)


output_file_path = "output_weasyprint.pdf"
generate_pdf(output_file_path)
