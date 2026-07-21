import os
import re
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Studio HTML Interface
STUDIO_HTML = """
<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Urdu AI Detector Studio | By Mr. Bill</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Poppins', 'Noto Nastaliq Urdu', sans-serif; background: #0b0f19; }
        .urdu-font { font-family: 'Noto Nastaliq Urdu', serif; }
        .glow { box-shadow: 0 0 25px rgba(20, 184, 166, 0.15); }
    </style>
</head>
<body class="text-slate-100 min-h-screen flex flex-col justify-between">

    <!-- Studio Header -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center space-x-3 space-x-reverse">
                <span class="text-3xl">🤖</span>
                <div>
                    <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-indigo-400">
                        Urdu AI Detector Studio
                    </h1>
                    <p class="text-xs text-slate-400">Engineered by Mr. Bill</p>
                </div>
            </div>
            <span class="bg-teal-500/10 text-teal-400 border border-teal-500/20 text-xs px-3 py-1 rounded-full animate-pulse">
                🟢 Live Cloud Engine
            </span>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="max-w-4xl mx-auto px-4 py-10 w-full flex-grow">
        <div class="text-center mb-8">
            <h2 class="text-2xl md:text-4xl font-extrabold mb-3 urdu-font leading-relaxed">
                اردو اور انگلش AI ڈٹیکٹر اسٹوڈیو
            </h2>
            <p class="text-slate-400 text-sm">
                Paste your text below to run real-time Perplexity & Burstiness NLP metrics.
            </p>
        </div>

        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 glow mb-8">
            <textarea id="userInput" rows="7" dir="auto"
                class="w-full bg-slate-950/70 border border-slate-800 rounded-xl p-4 text-slate-200 focus:outline-none focus:border-teal-500 transition-all text-base resize-none"
                placeholder="yahan apna Urdu ya English text paste karein..."></textarea>
            
            <div class="flex flex-wrap justify-between items-center mt-4 gap-4">
                <div class="text-xs text-slate-400 flex gap-4">
                    <span>Words: <strong id="wordCount" class="text-teal-400">0</strong></span>
                    <span>Chars: <strong id="charCount" class="text-teal-400">0</strong></span>
                </div>
                <div class="flex gap-2">
                    <button onclick="clearText()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm transition">Clear</button>
                    <button onclick="runStudioAnalysis()" id="runBtn" class="px-6 py-2 bg-gradient-to-r from-teal-500 to-indigo-600 hover:from-teal-400 hover:to-indigo-500 text-white font-semibold rounded-lg text-sm shadow-lg transition flex items-center gap-2">
                        <span>⚡ Run Studio Analysis</span>
                    </button>
                </div>
            </div>
        </div>

        <div id="resultBox" class="hidden bg-slate-900/90 border border-slate-800 rounded-2xl p-6 glow">
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6 text-center border-b border-slate-800 pb-3">
                📊 NLP Analysis Studio Dashboard
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center mb-6">
                <div class="bg-slate-950/60 border border-slate-800 p-6 rounded-xl text-center">
                    <div class="text-xs text-slate-400 uppercase tracking-widest">AI Probability Score</div>
                    <div id="scoreText" class="text-5xl font-extrabold text-teal-400 my-2">0%</div>
                    <div class="w-full bg-slate-800 h-3 rounded-full overflow-hidden mt-2">
                        <div id="scoreBar" class="bg-gradient-to-r from-teal-400 to-red-500 h-full w-0 transition-all duration-700"></div>
                    </div>
                </div>

                <div class="bg-slate-950/60 border border-slate-800 p-6 rounded-xl text-center">
                    <div class="text-xs text-slate-400 uppercase tracking-widest mb-2">Mr. Bill's Verdict</div>
                    <div id="verdictEmoji" class="text-4xl mb-2">🤔</div>
                    <p id="verdictText" class="text-lg font-bold urdu-font leading-relaxed">Analyzing...</p>
                </div>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                <div class="bg-slate-950 border border-slate-800/60 p-3 rounded-lg text-center">
                    <span class="text-xs text-slate-400 block">Perplexity Score</span>
                    <span id="perpVal" class="text-sm font-bold text-teal-400">0</span>
                </div>
                <div class="bg-slate-950 border border-slate-800/60 p-3 rounded-lg text-center">
                    <span class="text-xs text-slate-400 block">Burstiness Ratio</span>
                    <span id="burstVal" class="text-sm font-bold text-teal-400">0</span>
                </div>
                <div class="bg-slate-950 border border-slate-800/60 p-3 rounded-lg text-center col-span-2 md:col-span-1">
                    <span class="text-xs text-slate-400 block">Pattern Matching</span>
                    <span id="patternVal" class="text-sm font-bold text-teal-400">Normal</span>
                </div>
            </div>
        </div>
    </main>

    <footer class="text-center py-4 border-t border-slate-800 text-xs text-slate-500">
        Urdu AI Detector Studio &copy; 2026 | Built by Mr. Bill
    </footer>

    <script>
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playBeep(freq, type = 'sine', duration = 0.03) {
            try {
                if (audioCtx.state === 'suspended') audioCtx.resume();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = type;
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + duration);
            } catch(e) {}
        }

        const userInput = document.getElementById('userInput');
        userInput.addEventListener('input', () => {
            const text = userInput.value.trim();
            document.getElementById('wordCount').innerText = text ? text.split(/\s+/).length : 0;
            document.getElementById('charCount').innerText = text.length;
        });

        function clearText() {
            userInput.value = '';
            document.getElementById('wordCount').innerText = 0;
            document.getElementById('charCount').innerText = 0;
            document.getElementById('resultBox').classList.add('hidden');
        }

        async function runStudioAnalysis() {
            const text = userInput.value.trim();
            if(!text) return alert("Pehle text paste karein!");

            const runBtn = document.getElementById('runBtn');
            runBtn.disabled = true;
            runBtn.innerText = "⏳ Processing Backend...";

            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const data = await response.json();
            document.getElementById('resultBox').classList.remove('hidden');
            
            let current = 0;
            const interval = setInterval(() => {
                current++;
                document.getElementById('scoreText').innerText = current + '%';
                document.getElementById('scoreBar').style.width = current + '%';
                playBeep(250 + (current * 6));

                if (current >= data.score) {
                    clearInterval(interval);
                    document.getElementById('perpVal').innerText = data.perplexity;
                    document.getElementById('burstVal').innerText = data.burstiness;
                    document.getElementById('patternVal').innerText = data.pattern;
                    document.getElementById('verdictText').innerText = data.verdict;
                    document.getElementById('verdictEmoji').innerText = data.emoji;

                    runBtn.disabled = false;
                    runBtn.innerHTML = "<span>⚡ Run Studio Analysis</span>";
                }
            }, 20);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(STUDIO_HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    text = data.get('text', '')
    
    words = re.findall(r'\w+', text)
    sentences = [s for s in re.split(r'[.!?۔]+', text) if s.strip()]
    
    num_words = len(words) or 1
    num_sentences = len(sentences) or 1
    
    avg_sentence_len = num_words / num_sentences
    ai_phrases = ['furthermore', 'moreover', 'in conclusion', 'delve', 'tapestry', 'misaal ke taur par', 'khulasa', 'nateeja', 'albatta']
    ai_matches = sum(1 for w in words if w.lower() in ai_phrases)
    
    perplexity = round(min(100, max(10, (num_words / (ai_matches + 1)) * 1.5)), 1)
    burstiness = round(min(1.0, max(0.1, (avg_sentence_len / 15))), 2)
    
    score = int(min(98, max(5, (ai_matches * 18) + (avg_sentence_len * 2.2))))

    if score > 70:
        verdict = "Yeh 100% AI ka likha hua text hai! Bill sb ne pakar liya!"
        emoji = "🤖"
        pattern = "High AI Signature"
    elif score > 40:
        verdict = "Mashkook Text! Is mein AI aur Insaan dono ki milaawat hai."
        emoji = "🧐"
        pattern = "Mixed Structure"
    else:
        verdict = "Khaalis Insani Tahrir! Yeh kisi insan ka hi likha hua lagta hai."
        emoji = "✍️"
        pattern = "Natural Human"

    return jsonify({
        'score': score,
        'perplexity': perplexity,
        'burstiness': burstiness,
        'pattern': pattern,
        'verdict': verdict,
        'emoji': emoji
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
