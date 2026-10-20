from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods = ['GET', 'POST'])
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

    return render_template('index.html', result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
