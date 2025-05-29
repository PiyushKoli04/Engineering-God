import markdown
from flask import Flask, render_template, request
from RealTimeSearchEngine import RealtimeSearchEngine

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    answer = ""
    if request.method == "POST":
        prompt = request.form.get("prompt")
        raw_answer = RealtimeSearchEngine(prompt)

        # Convert Markdown with line breaks preserved
        answer = markdown.markdown(
            raw_answer,
            extensions=['markdown.extensions.extra'],
            output_format='html5'
        ).replace('\n', '<br>')  # Preserve extra newlines if any

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
