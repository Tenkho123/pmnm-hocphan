from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def menu():
    return render_template('menu.html')

@app.route("/calculator", methods = ['GET', 'POST'])
def calculator():
    result, error = None, None
    flag = False

    if request.method == 'POST':
        num_a, num_b = 0, 0

        try:
            text_a = request.form.get('a').replace(",", ".")
            num_a = float(text_a)
        except (ValueError, TypeError):
            error = "Lỗi ô a: Vui lòng nhập một số"
            flag = True

        try: 
            num_b = float(request.form.get('b'))
        except (ValueError, TypeError):
            error = "Lỗi ô b: Vui lòng nhập một số"
            flag = True

        if (not flag):
            try:
                operator = request.form.get('op')

                if operator == '+':
                    result = num_a + num_b
                elif operator == '-':
                    result = num_a - num_b
                elif operator == '*':
                    result = num_a * num_b
                elif operator == '/':
                    if num_b == 0:
                        error = "Lỗi ô b: Không thể chia cho 0"
                    else:
                        result = num_a / num_b
                else:
                    error = "Phép toán không hợp lệ"
                    
            except (ValueError, TypeError):
                error = "A và B không phải số hợp lệ"

    return render_template('basiccalc.html', result=result, error=error)

@app.route("/score", methods = ['POST', 'GET'])
def ScoreCalculator():
    result, error = None, None

    if request.method == 'POST':
        try:
            tex_a = request.form.get('a').replace(",", ".")
            tex_b = request.form.get('b').replace(",", ".")
            tex_c = request.form.get('c').replace(",", ".")
            
            num_a, num_b, num_c = 0, 0, 0
            ErrorFlag = False

            try:
                num_a = float(tex_a)
            except (ValueError, TypeError):
                error = "Lỗi ô CC: Vui lòng nhập 1 số."
                ErrorFlag = True
            
            try:
                num_b = float(tex_b)
            except (ValueError, TypeError):
                error = "Lỗi ô GK: Vui lòng nhập 1 số."
                ErrorFlag = True

            try:
                num_c = float(tex_c)
            except (ValueError, TypeError):
                error = "Lỗi ô CK: Vui lòng nhập 1 số."
                ErrorFlag = True

            if (not ErrorFlag):
                calc = num_a / 10.0  * 1.0 + num_b / 10.0 * 3.0 + num_c / 10.0 * 6.0

                if not 0 <= num_a <= 10:
                    error = "Lỗi ô CC: Điểm phải từ 0 đến 10."
                    ErrorFlag = True
                
                elif not 0 <= num_b <= 10:
                    error = "Lỗi ô GK: Điểm phải từ 0 đến 10."
                    ErrorFlag = True

                elif not 0 <= num_c <= 10:
                    error = "Lỗi ô CK: Điểm phải từ 0 đến 10."
                    ErrorFlag = True

            
            if (not ErrorFlag):
                result = str(round(calc, 1)) + " | "

                if (num_a < 1 or num_b < 1 or num_c < 1):
                    result += "F (điểm thi dưới 1)"

                elif (calc >= 8.5):
                    result += "A"

                elif (calc >= 7.0):
                    result += "B"

                elif (calc >= 5.5):
                    result += "C"

                elif (calc >= 4.0):
                    result += "D"

                else:
                    result += "F"
                

        except (ValueError, TypeError):
            error = ValueError + " :: " + TypeError

    return render_template('diemhp.html', result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
