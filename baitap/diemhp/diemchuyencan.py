from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods = ['POST', 'GET'])
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

    return render_template('index.html', result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
