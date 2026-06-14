import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from generate_questions import generate_quiz_questions
from analysis import analyze_answers

load_dotenv()

try:
    from openai import AzureOpenAI
    _oai_client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY", ""),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    )
    OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    OPENAI_OK = bool(os.getenv("AZURE_OPENAI_KEY"))
except Exception:
    _oai_client = None
    OPENAI_OK = False

try:
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    _lang_client = TextAnalyticsClient(
        endpoint=os.getenv("AZURE_LANGUAGE_ENDPOINT", ""),
        credential=AzureKeyCredential(os.getenv("AZURE_LANGUAGE_KEY", "")),
    )
    LANGUAGE_OK = bool(os.getenv("AZURE_LANGUAGE_KEY"))
except Exception:
    _lang_client = None
    LANGUAGE_OK = False

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "questions_db.txt"
HISTORY_FILE = BASE_DIR / "history.txt"
RESULTS_FILE = BASE_DIR / "results.txt"
USERS_FILE = BASE_DIR / "users.json"


def _load_users():
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_users(users):
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


def _get_user(username):
    if not username:
        return None
    return _load_users().get(username)


def _create_user(username, password):
    users = _load_users()
    if username in users:
        return None
    users[username] = {
        "username": username,
        "password": password,
        "tests": []
    }
    _save_users(users)
    return users[username]

HTML = """
<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Adaptive IT Learning Hub</title>
<style>
:root{color-scheme:dark;font-family:Arial,sans-serif}
body{margin:0;background:linear-gradient(135deg,#07111f,#102a43);color:#eff6ff}
.page{max-width:1080px;margin:0 auto;padding:24px}
.card{background:rgba(15,23,42,0.86);border:1px solid #334155;border-radius:18px;padding:18px;margin-bottom:18px}
h1,h2,h3{margin-top:0}
.pill{display:inline-block;background:#1d4ed8;color:#eff6ff;padding:6px 10px;border-radius:999px;font-size:12px;text-transform:uppercase}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.btn{background:linear-gradient(135deg,#38bdf8,#2563eb);color:white;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:700;margin-right:8px}
.btn.secondary{background:linear-gradient(135deg,#f59e0b,#f97316)}
.muted{color:#cbd5e1;font-size:14px}
.topic{display:inline-block;padding:6px 8px;background:#0f172a;border-radius:8px;margin-right:6px;margin-top:6px;border:1px solid #1e293b}
.score-box{display:flex;gap:12px;flex-wrap:wrap}
.mini{background:#111827;border:1px solid #1f2937;padding:10px;border-radius:12px;min-width:120px}
.tag{color:#bfdbfe;font-size:12px;text-transform:uppercase}
textarea{width:100%;background:#0f172a;color:#eff6ff;border:1px solid #334155;border-radius:10px;padding:10px;font-size:14px;resize:vertical;box-sizing:border-box}
.ai-badge{display:inline-block;background:#064e3b;color:#6ee7b7;padding:3px 8px;border-radius:6px;font-size:11px;margin-left:8px}
</style></head><body>
<div class="page">
<div class="card">
<span class="pill">Adaptive Learning Tool for Pakistani IT Students</span>
<h1>Adaptive IT Learning Hub <span class="ai-badge">Azure OpenAI + Azure AI Language</span></h1>
<p class="muted">Built by Wajiha Imran · Bahauddin Zakariya University · BS IT 1st Year (Completed) · GPA 4.0 · Built solo in 4 days</p>
<div class="score-box">
<div class="mini"><div class="tag">Problem</div><div id="problemText">Limited access to personalised exam prep</div></div>
<div class="mini"><div class="tag">AI</div><div id="aiText">Adaptive difficulty + weak-topic insight</div></div>
<div class="mini"><div class="tag">Outcome</div><div id="outcomeText">Better revision paths for every student</div></div>
</div>
<button class="btn" onclick="toggleLanguage()" id="langBtn" style="margin-top:12px">Urdu / English</button>
</div>
<div class="grid">
<div class="card">
<h2>Launch a practice session</h2>
<p class="muted">Azure OpenAI generates a personalised adaptive insight.</p>
<button class="btn" onclick="loadDemo()">Generate AI Insight</button>
<button class="btn secondary" onclick="location.href='/api/health'">API Health</button>
</div>
<div class="card" id="insightBox">
<h3 id="insightTitle">Current AI Insight</h3>
<p class="muted" id="insightBody">Click the button to see an adaptive recommendation.</p>
</div>
</div>
<div class="card">
  <h2>Start a Quiz</h2>
  <p class="muted">Choose a subject and difficulty level. Each level has 10 questions.</p>
  <div id="quizMenu">
    <div class="grid">
      <div class="card" style="margin-bottom:0"><h3>🐍 Python</h3>
        <button class="btn" onclick="startQuiz('Python','Beginner')">Beginner</button>
        <button class="btn" onclick="startQuiz('Python','Intermediate')">Intermediate</button>
        <button class="btn" onclick="startQuiz('Python','Advanced')">Advanced</button>
      </div>
      <div class="card" style="margin-bottom:0"><h3>💻 Programming Basics</h3>
        <button class="btn" onclick="startQuiz('Basics','Beginner')">Beginner</button>
        <button class="btn" onclick="startQuiz('Basics','Intermediate')">Intermediate</button>
        <button class="btn" onclick="startQuiz('Basics','Advanced')">Advanced</button>
      </div>
      <div class="card" style="margin-bottom:0"><h3>➗ Mathematics</h3>
        <button class="btn" onclick="startQuiz('Math','Beginner')">Beginner</button>
        <button class="btn" onclick="startQuiz('Math','Intermediate')">Intermediate</button>
        <button class="btn" onclick="startQuiz('Math','Advanced')">Advanced</button>
      </div>
      <div class="card" style="margin-bottom:0"><h3>🗄️ Data Structures</h3>
        <button class="btn" onclick="startQuiz('DSA','Beginner')">Beginner</button>
        <button class="btn" onclick="startQuiz('DSA','Intermediate')">Intermediate</button>
        <button class="btn" onclick="startQuiz('DSA','Advanced')">Advanced</button>
      </div>
    </div>
  </div>
  <div id="quizBox" style="display:none;margin-top:16px">
    <h3 id="quizTitle"></h3>
    <p class="muted" id="quizProgress"></p>
    <div id="quizQuestion" class="card" style="margin-bottom:12px"></div>
    <div id="quizOptions"></div>
    <button class="btn" id="nextBtn" onclick="nextQuestion()" style="margin-top:12px;display:none">Next</button>
    <div id="quizResult" style="margin-top:12px"></div>
  </div>
</div>

<div class="card">
<h2>Analyse your answers</h2>
<p class="muted">Paste answers below. Azure AI Language detects your weak topics.</p>
<textarea id="answersInput" rows="4" placeholder="e.g. I got confused about recursion and loops..."></textarea>
<button class="btn" onclick="analyzeAnswers()" style="margin-top:10px">Detect Weak Topics</button>
<div id="analyzeResult" style="margin-top:12px"></div>
</div>
<div class="card">
<h2 id="analyticsTitle">Teacher analytics snapshot</h2>
<div id="analyticsBox" class="score-box"></div>
</div>
</div>
<script>
const T={en:{problem:"Limited access to personalised exam prep",ai:"Adaptive difficulty + weak-topic insight",outcome:"Better revision paths for every student",insightTitle:"Current AI Insight",insightBody:"Click the button to see an adaptive recommendation.",analyticsTitle:"Teacher analytics snapshot"},ur:{problem:"ذاتی امتحانی تیاری تک محدود رسائی",ai:"موافقتی مشکل اور کمزور موضوعات کی بصیرت",outcome:"ہر طالب علم کے لیے بہتر ریویژن راستہ",insightTitle:"موجودہ AI بصیرت",insightBody:"بٹن دبائیں۔",analyticsTitle:"استاد کے تجزیاتی جائزہ"}};
let lang="en";
function toggleLanguage(){lang=lang==="en"?"ur":"en";const t=T[lang];document.getElementById("problemText").textContent=t.problem;document.getElementById("aiText").textContent=t.ai;document.getElementById("outcomeText").textContent=t.outcome;document.getElementById("insightTitle").textContent=t.insightTitle;document.getElementById("insightBody").textContent=t.insightBody;document.getElementById("analyticsTitle").textContent=t.analyticsTitle;document.getElementById("langBtn").textContent=lang==="en"?"Urdu / English":"English / Urdu";}
function loadDemo(){document.getElementById("insightBody").textContent="Generating...";fetch("/api/demo").then(r=>r.json()).then(data=>{document.getElementById("insightBox").innerHTML="<h3>Current AI Insight <span class=\"ai-badge\">Azure OpenAI</span></h3><p>"+data.message+"</p><p class=\"muted\">Focus: "+data.focus+"</p>";});}
function analyzeAnswers(){const text=document.getElementById("answersInput").value.trim();if(!text){alert("Enter some answers first.");return;}document.getElementById("analyzeResult").innerHTML="<p class=\"muted\">Analysing...</p>";fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({answers:[text]})}).then(r=>r.json()).then(data=>{document.getElementById("analyzeResult").innerHTML="<div class=\"mini\"><div class=\"tag\">Weak Topics <span class=\"ai-badge\">Azure AI Language</span></div><div style=\"margin-top:6px\">"+(data.weak_topics.join(", ")||"None detected")+"</div><div class=\"muted\" style=\"margin-top:6px\">"+data.advice+"</div></div>";});}

const QUESTIONS = {
  "Python": {
    "Beginner": [
      {q:"What is the output of print(2+3)?",o:["5","23","Error","None"],a:0},
      {q:"Which keyword defines a function in Python?",o:["func","def","function","define"],a:1},
      {q:"What data type is 3.14?",o:["int","str","float","bool"],a:2},
      {q:"How do you create a list in Python?",o:["{}","()","[]","<>"],a:2},
      {q:"What does len('hello') return?",o:["4","5","6","Error"],a:1},
      {q:"Which symbol is used for comments in Python?",o:["//","#","/*","--"],a:1},
      {q:"What is the output of type(True)?",o:["int","bool","str","NoneType"],a:1},
      {q:"How do you start a for loop in Python?",o:["for i in range:","for(i=0;i<n;i++)","for i in range(n):","loop i to n:"],a:2},
      {q:"What does print() do?",o:["Takes input","Shows output","Defines variable","None"],a:1},
      {q:"Which of these is a valid variable name?",o:["2name","my-var","my_var","class"],a:2}
    ],
    "Intermediate": [
      {q:"What is a lambda function?",o:["A class method","An anonymous function","A loop","A module"],a:1},
      {q:"What does *args do in a function?",o:["Passes keyword args","Passes variable positional args","Multiplies args","None"],a:1},
      {q:"What is list comprehension?",o:["A way to copy lists","A concise way to create lists","A sorting method","A search method"],a:1},
      {q:"What does 'self' refer to in a class?",o:["The class itself","The current instance","A method","A variable"],a:1},
      {q:"What is the output of [1,2,3][::-1]?",o:["[1,2,3]","[3,2,1]","Error","[]"],a:1},
      {q:"Which module is used for regular expressions?",o:["re","regex","regexp","match"],a:0},
      {q:"What does try/except do?",o:["Loops code","Handles errors","Defines functions","Imports modules"],a:1},
      {q:"What is a dictionary in Python?",o:["Ordered list","Key-value pairs","A set","A tuple"],a:1},
      {q:"What does 'import os' do?",o:["Imports operating system module","Creates a file","Runs a program","None"],a:0},
      {q:"What is the difference between == and is?",o:["No difference","== checks value, is checks identity","is checks value","None"],a:1}
    ],
    "Advanced": [
      {q:"What is a generator in Python?",o:["A function that returns a list","A function using yield","A class decorator","A module"],a:1},
      {q:"What is the GIL in Python?",o:["Global Import Lock","Global Interpreter Lock","General Input Loop","None"],a:1},
      {q:"What does @property decorator do?",o:["Makes a method private","Allows method to be accessed like attribute","Creates a class","None"],a:1},
      {q:"What is monkey patching?",o:["Debugging technique","Modifying code at runtime","A design pattern","None"],a:1},
      {q:"What is __slots__ used for?",o:["Memory optimisation","Error handling","Importing","None"],a:0},
      {q:"What does collections.defaultdict do?",o:["Sorts a dict","Provides default value for missing keys","Merges dicts","None"],a:1},
      {q:"What is asyncio used for?",o:["Multithreading","Asynchronous programming","Database access","None"],a:1},
      {q:"What is a metaclass?",o:["A class of a class","A base class","An abstract class","None"],a:0},
      {q:"What does functools.lru_cache do?",o:["Clears cache","Caches function results","Limits recursion","None"],a:1},
      {q:"What is the purpose of __init__.py?",o:["Runs on import","Marks directory as package","Both","None"],a:2}
    ]
  },
  "Programming Basics": {
    "Beginner": [
      {q:"What is a variable?",o:["A fixed value","A container for data","A function","A loop"],a:1},
      {q:"What is an algorithm?",o:["A programming language","A step-by-step solution","A data type","A compiler"],a:1},
      {q:"What does CPU stand for?",o:["Central Process Unit","Central Processing Unit","Computer Processing Unit","None"],a:1},
      {q:"What is a compiler?",o:["Translates code to machine language","Runs code line by line","Stores data","None"],a:0},
      {q:"What is binary?",o:["Base 10 number system","Base 2 number system","Base 16","None"],a:1},
      {q:"What is an IDE?",o:["Internet Data Exchange","Integrated Development Environment","Internal Debug Engine","None"],a:1},
      {q:"What is a loop used for?",o:["Store data","Repeat code","Define functions","None"],a:1},
      {q:"What is a boolean?",o:["A number","True or False value","A string","None"],a:1},
      {q:"What is debugging?",o:["Writing code","Finding and fixing errors","Compiling","None"],a:1},
      {q:"What is syntax?",o:["Logic of code","Rules of a programming language","A data structure","None"],a:1}
    ],
    "Intermediate": [
      {q:"What is recursion?",o:["A loop","A function calling itself","A data type","None"],a:1},
      {q:"What is OOP?",o:["Object Oriented Programming","Open Output Process","None","Online Output Program"],a:0},
      {q:"What is inheritance in OOP?",o:["Copying code","A class acquiring properties of another","A loop","None"],a:1},
      {q:"What is encapsulation?",o:["Hiding internal details","Sharing data","A loop","None"],a:0},
      {q:"What is polymorphism?",o:["Many forms of a function/class","A data type","A module","None"],a:0},
      {q:"What is a stack data structure?",o:["FIFO","LIFO","Random access","None"],a:1},
      {q:"What is a queue?",o:["LIFO","FIFO","Random","None"],a:1},
      {q:"What is Big O notation?",o:["A loop","Algorithm efficiency measurement","A data type","None"],a:1},
      {q:"What is abstraction?",o:["Hiding complexity","Showing all details","A loop","None"],a:0},
      {q:"What is a linked list?",o:["Array","Nodes connected by pointers","A queue","None"],a:1}
    ],
    "Advanced": [
      {q:"What is dynamic programming?",o:["Using dynamic variables","Solving problems by breaking into subproblems","A language","None"],a:1},
      {q:"What is a binary search tree?",o:["A tree where left < root < right","A random tree","A graph","None"],a:0},
      {q:"What is time complexity of binary search?",o:["O(n)","O(log n)","O(n2)","O(1)"],a:1},
      {q:"What is a hash table?",o:["A sorted array","Key-value store with hash function","A tree","None"],a:1},
      {q:"What is a graph in CS?",o:["A chart","Nodes connected by edges","A matrix","None"],a:1},
      {q:"What is Dijkstras algorithm used for?",o:["Sorting","Shortest path","Searching","None"],a:1},
      {q:"What is a deadlock?",o:["A bug","Two processes waiting for each other forever","A loop","None"],a:1},
      {q:"What is memoisation?",o:["Memory management","Caching results of expensive calls","Garbage collection","None"],a:1},
      {q:"What is a semaphore?",o:["A signal","Synchronisation tool for threads","A data type","None"],a:1},
      {q:"What is the difference between process and thread?",o:["No difference","Process is independent, thread shares memory","Thread is independent","None"],a:1}
    ]
  },
  "Mathematics": {
    "Beginner": [
      {q:"What is 15% of 200?",o:["25","30","35","40"],a:1},
      {q:"What is the square root of 144?",o:["10","11","12","13"],a:2},
      {q:"What is 2 to the power of 8?",o:["128","256","512","64"],a:1},
      {q:"What is the value of pi (approx)?",o:["3.14","2.71","1.61","4.13"],a:0},
      {q:"What is a prime number?",o:["Divisible by 2","Only divisible by 1 and itself","Even number","None"],a:1},
      {q:"What is the mean of 2,4,6,8,10?",o:["5","6","7","8"],a:1},
      {q:"What is 12 factorial (12!)?",o:["479001600","39916800","3628800","None"],a:0},
      {q:"What is a set in mathematics?",o:["Ordered collection","Unordered collection of unique elements","A sequence","None"],a:1},
      {q:"What is the area of a circle with radius 7?",o:["154","144","164","134"],a:0},
      {q:"What is a logarithm?",o:["Inverse of exponentiation","A type of loop","A matrix","None"],a:0}
    ],
    "Intermediate": [
      {q:"What is a matrix?",o:["A single number","A 2D array of numbers","A vector","None"],a:1},
      {q:"What is the determinant of [[1,2],[3,4]]?",o:["-2","2","-4","4"],a:0},
      {q:"What is Boolean algebra used for?",o:["Statistics","Logic circuits and CS","Calculus","None"],a:1},
      {q:"What is modular arithmetic?",o:["Division","Remainder after division","Multiplication","None"],a:1},
      {q:"What is a permutation?",o:["Ordered arrangement","Unordered selection","A set","None"],a:0},
      {q:"What is a combination?",o:["Ordered selection","Unordered selection","A sequence","None"],a:1},
      {q:"What is the Pythagorean theorem?",o:["a+b=c","a2+b2=c2","a*b=c","None"],a:1},
      {q:"What is a derivative in calculus?",o:["Area under curve","Rate of change","A constant","None"],a:1},
      {q:"What is an integral?",o:["Rate of change","Area under curve","A matrix","None"],a:1},
      {q:"What is a probability?",o:["Certainty","Likelihood of event between 0 and 1","A percentage only","None"],a:1}
    ],
    "Advanced": [
      {q:"What is Big O of bubble sort?",o:["O(n)","O(n log n)","O(n2)","O(1)"],a:2},
      {q:"What is a Fourier transform used for?",o:["Sorting","Signal analysis","Matrix multiplication","None"],a:1},
      {q:"What is linear algebra used for in ML?",o:["Storing data","Vector and matrix operations","None","Loops"],a:1},
      {q:"What is gradient descent?",o:["A sorting algorithm","Optimisation algorithm for ML","A data structure","None"],a:1},
      {q:"What is a normal distribution?",o:["Uniform spread","Bell curve distribution","Random data","None"],a:1},
      {q:"What is eigenvalue?",o:["A scalar for linear transformation","A matrix","A vector","None"],a:0},
      {q:"What is entropy in information theory?",o:["Energy","Measure of uncertainty","A constant","None"],a:1},
      {q:"What is Bayes theorem used for?",o:["Sorting","Updating probability with new evidence","Matrix ops","None"],a:1},
      {q:"What is a p-value in statistics?",o:["Probability of results given null hypothesis","A percentage","A constant","None"],a:0},
      {q:"What is the chain rule in calculus?",o:["Adding derivatives","Differentiating composite functions","Integration","None"],a:1}
    ]
  },
  "Data Structures": {
    "Beginner": [
      {q:"What is an array?",o:["Key-value store","Collection of elements in sequence","A tree","None"],a:1},
      {q:"What is a stack?",o:["FIFO structure","LIFO structure","A graph","None"],a:1},
      {q:"What is a queue?",o:["LIFO","FIFO","Random access","None"],a:1},
      {q:"What is a linked list node made of?",o:["Only data","Data and pointer to next node","Only pointer","None"],a:1},
      {q:"What is the index of first element in array?",o:["1","0","-1","None"],a:1},
      {q:"What is a tree?",o:["Linear structure","Hierarchical structure","A graph","None"],a:1},
      {q:"What is a leaf node in a tree?",o:["Root node","Node with no children","Node with two children","None"],a:1},
      {q:"What operation adds to a stack?",o:["enqueue","push","insert","add"],a:1},
      {q:"What operation removes from a stack?",o:["dequeue","pop","remove","delete"],a:1},
      {q:"What is a hash table used for?",o:["Sorting","Fast key-value lookup","Traversal","None"],a:1}
    ],
    "Intermediate": [
      {q:"What is a binary search tree?",o:["Random tree","Left < root < right","A graph","None"],a:1},
      {q:"What is time complexity of array access?",o:["O(n)","O(1)","O(log n)","None"],a:1},
      {q:"What is a heap?",o:["A stack","Tree-based structure for priority queue","A graph","None"],a:1},
      {q:"What is DFS?",o:["Depth First Search","Data File System","None","Direct File Search"],a:0},
      {q:"What is BFS?",o:["Breadth First Search","Binary File System","None","Base File Search"],a:0},
      {q:"What is a doubly linked list?",o:["Single pointer nodes","Nodes with next and prev pointers","A tree","None"],a:1},
      {q:"What is a circular queue?",o:["Queue in a circle shape","Queue where tail connects to head","A stack","None"],a:1},
      {q:"What is amortised analysis?",o:["Worst case only","Average cost over sequence of operations","Best case","None"],a:1},
      {q:"What is a trie?",o:["A graph","Tree for storing strings by prefix","A hash table","None"],a:1},
      {q:"What is a priority queue?",o:["Random queue","Queue where highest priority served first","A stack","None"],a:1}
    ],
    "Advanced": [
      {q:"What is an AVL tree?",o:["Unbalanced BST","Self-balancing BST","A heap","None"],a:1},
      {q:"What is the time complexity of heapify?",o:["O(n)","O(log n)","O(n log n)","O(1)"],a:0},
      {q:"What is a red-black tree?",o:["A coloured graph","Self-balancing BST with colour rules","A heap","None"],a:1},
      {q:"What is a segment tree used for?",o:["Sorting","Range queries on arrays","Graph traversal","None"],a:1},
      {q:"What is a Fenwick tree?",o:["A graph","Binary indexed tree for prefix sums","A heap","None"],a:1},
      {q:"What is the time complexity of merge sort?",o:["O(n2)","O(n log n)","O(n)","O(log n)"],a:1},
      {q:"What is a sparse table?",o:["Empty table","Structure for range minimum queries","A hash table","None"],a:1},
      {q:"What is topological sorting?",o:["Sorting numbers","Ordering DAG nodes by dependencies","A tree traversal","None"],a:1},
      {q:"What is a disjoint set?",o:["A graph","Union-Find data structure","A tree","None"],a:1},
      {q:"What is the time complexity of quick sort average case?",o:["O(n2)","O(n log n)","O(n)","O(log n)"],a:1}
    ]
  },
  "Networking": {
    "Beginner": [
      {q:"What does IP stand for?",o:["Internet Protocol","Internal Process","Input Port","None"],a:0},
      {q:"What is a router?",o:["Stores data","Directs network traffic","Displays web pages","None"],a:1},
      {q:"What does HTTP stand for?",o:["HyperText Transfer Protocol","High Transfer Protocol","None","Host Transfer Process"],a:0},
      {q:"What is a MAC address?",o:["Software address","Hardware address of network interface","IP address","None"],a:1},
      {q:"What does DNS stand for?",o:["Domain Name System","Data Network Service","None","Direct Name Server"],a:0},
      {q:"What is a firewall?",o:["A physical wall","Security system filtering network traffic","A router","None"],a:1},
      {q:"What is bandwidth?",o:["Speed of CPU","Data transfer capacity of network","Memory size","None"],a:1},
      {q:"What is Wi-Fi?",o:["Wired connection","Wireless network technology","A protocol","None"],a:1},
      {q:"What is a server?",o:["A client machine","Computer providing services to other computers","A router","None"],a:1},
      {q:"What is a packet?",o:["A physical package","Unit of data in a network","A protocol","None"],a:1}
    ],
    "Intermediate": [
      {q:"What is TCP vs UDP?",o:["Both reliable","TCP reliable, UDP faster but unreliable","UDP reliable","None"],a:1},
      {q:"What is the OSI model?",o:["A protocol","7-layer network communication framework","A hardware standard","None"],a:1},
      {q:"What is subnetting?",o:["Connecting networks","Dividing network into smaller sub-networks","A protocol","None"],a:1},
      {q:"What is DHCP?",o:["Dynamic Host Configuration Protocol","Direct Host Control","None","Data Host Connection"],a:0},
      {q:"What is a VPN?",o:["Virtual Private Network","Very Private Node","None","Virtual Public Network"],a:0},
      {q:"What is ARP?",o:["Address Resolution Protocol","Auto Routing Protocol","None","Automatic Request Protocol"],a:0},
      {q:"What is a socket?",o:["A hardware port","Endpoint for network communication","A protocol","None"],a:1},
      {q:"What is NAT?",o:["Network Address Translation","Node Access Table","None","Network Automation Tool"],a:0},
      {q:"What is latency?",o:["Bandwidth","Delay in data transmission","Speed","None"],a:1},
      {q:"What is a proxy server?",o:["A firewall","Intermediary between client and server","A router","None"],a:1}
    ],
    "Advanced": [
      {q:"What is BGP?",o:["Border Gateway Protocol","Basic Graph Protocol","None","Binary Gateway Process"],a:0},
      {q:"What is OSPF?",o:["Open Shortest Path First","Optional Secure Protocol","None","Output Signal Path"],a:0},
      {q:"What is a VLAN?",o:["Virtual LAN","Very Large Area Network","None","Virtual Link Access Node"],a:0},
      {q:"What is SSL/TLS used for?",o:["Routing","Encrypting network communication","Compression","None"],a:1},
      {q:"What is a CDN?",o:["Content Delivery Network","Central Data Node","None","Core Distribution Network"],a:0},
      {q:"What is QoS?",o:["Quality of Service","Queue of Servers","None","Query on System"],a:0},
      {q:"What is MPLS?",o:["Multi Protocol Label Switching","Main Protocol Layer","None","Multi Path Local Switch"],a:0},
      {q:"What is a zero-day vulnerability?",o:["A known bug","Unknown vulnerability with no patch","A firewall rule","None"],a:1},
      {q:"What is anycast routing?",o:["Broadcasting","Routing to nearest node in a group","Multicasting","None"],a:1},
      {q:"What is a SYN flood attack?",o:["A virus","DDoS attack exploiting TCP handshake","A worm","None"],a:1}
    ]
  },
  "Database": {
    "Beginner": [
      {q:"What does SQL stand for?",o:["Structured Query Language","Simple Query Logic","None","System Query Layer"],a:0},
      {q:"What is a primary key?",o:["Any column","Unique identifier for a row","A foreign key","None"],a:1},
      {q:"What does SELECT do in SQL?",o:["Deletes data","Retrieves data","Updates data","None"],a:1},
      {q:"What is a table in a database?",o:["A chart","Organised rows and columns of data","A query","None"],a:1},
      {q:"What does INSERT do?",o:["Updates rows","Adds new rows","Deletes rows","None"],a:1},
      {q:"What does DELETE do?",o:["Updates rows","Adds rows","Removes rows","None"],a:2},
      {q:"What is a foreign key?",o:["A primary key","References primary key of another table","A unique key","None"],a:1},
      {q:"What does WHERE clause do?",o:["Sorts data","Filters rows based on condition","Groups data","None"],a:1},
      {q:"What is NULL in SQL?",o:["Zero","Empty string","Missing or unknown value","None"],a:2},
      {q:"What does ORDER BY do?",o:["Filters","Sorts results","Groups","None"],a:1}
    ],
    "Intermediate": [
      {q:"What is a JOIN in SQL?",o:["Splits tables","Combines rows from multiple tables","Deletes tables","None"],a:1},
      {q:"What is normalisation?",o:["Making database faster","Organising to reduce redundancy","Backing up","None"],a:1},
      {q:"What is an index in a database?",o:["A primary key","Structure to speed up queries","A table","None"],a:1},
      {q:"What is ACID?",o:["A chemical","Atomicity, Consistency, Isolation, Durability","A protocol","None"],a:1},
      {q:"What is a stored procedure?",o:["A table","Saved SQL code that can be executed","A view","None"],a:1},
      {q:"What is a view in SQL?",o:["A table copy","Virtual table based on a query","A stored procedure","None"],a:1},
      {q:"What does GROUP BY do?",o:["Sorts data","Groups rows sharing a value","Filters data","None"],a:1},
      {q:"What is a transaction?",o:["A query","Unit of work that is all-or-nothing","A table","None"],a:1},
      {q:"What is referential integrity?",o:["Data accuracy","Foreign key always refers to valid primary key","None","Backup"],a:1},
      {q:"What is the difference between INNER and LEFT JOIN?",o:["No difference","INNER returns matches only, LEFT returns all left rows","None","RIGHT returns all"],a:1}
    ],
    "Advanced": [
      {q:"What is query optimisation?",o:["Writing longer queries","Improving query performance","Normalisation","None"],a:1},
      {q:"What is a clustered index?",o:["Non-unique index","Index that sorts and stores data rows","A foreign key","None"],a:1},
      {q:"What is sharding?",o:["Backing up","Splitting database across multiple machines","Normalisation","None"],a:1},
      {q:"What is CAP theorem?",o:["A sorting algorithm","Consistency, Availability, Partition tolerance tradeoff","A protocol","None"],a:1},
      {q:"What is a NoSQL database?",o:["A bad database","Non-relational database","SQL without joins","None"],a:1},
      {q:"What is database replication?",o:["Deleting copies","Copying database to multiple servers","Normalisation","None"],a:1},
      {q:"What is an ORM?",o:["A query language","Object Relational Mapper","A database type","None"],a:1},
      {q:"What is eventual consistency?",o:["Immediate consistency","System will become consistent over time","ACID property","None"],a:1},
      {q:"What is a materialized view?",o:["A virtual table","Stored result of a query updated periodically","A stored procedure","None"],a:1},
      {q:"What is connection pooling?",o:["Network setting","Reusing database connections for efficiency","A join type","None"],a:1}
    ]
  }
};

let currentSubject = "", currentLevel = "", currentIndex = 0, score = 0, answered = false;

function startQuiz(subject, level) {
  currentSubject = subject;
  currentLevel = level;
  currentIndex = 0;
  score = 0;
  answered = false;
  document.getElementById("quizMenu").style.display = "none";
  document.getElementById("quizBox").style.display = "block";
  document.getElementById("quizResult").innerHTML = "";
  showQuestion();
}

function showQuestion() {
  const qs = QUESTIONS[currentSubject][currentLevel];
  const q = qs[currentIndex];
  answered = false;
  document.getElementById("quizTitle").textContent = currentSubject + " — " + currentLevel;
  document.getElementById("quizProgress").textContent = "Question " + (currentIndex+1) + " of 10 | Score: " + score;
  document.getElementById("quizQuestion").innerHTML = "<p style=\"font-size:16px;margin:0\">" + q.q + "</p>";
  document.getElementById("nextBtn").style.display = "none";
  const opts = document.getElementById("quizOptions");
  opts.innerHTML = q.o.map((opt, i) =>
    "<button class=\"btn\" style=\"display:block;width:100%;margin-bottom:8px;text-align:left;background:rgba(15,23,42,0.9);border:1px solid #334155\" onclick=\"checkAnswer(" + i + ")\">" + opt + "</button>"
  ).join("");
}

function checkAnswer(selected) {
  if (answered) return;
  answered = true;
  const qs = QUESTIONS[currentSubject][currentLevel];
  const q = qs[currentIndex];
  const btns = document.getElementById("quizOptions").querySelectorAll("button");
  btns.forEach((btn, i) => {
    btn.disabled = true;
    if (i === q.a) btn.style.background = "linear-gradient(135deg,#166534,#15803d)";
    else if (i === selected && selected !== q.a) btn.style.background = "linear-gradient(135deg,#7f1d1d,#991b1b)";
  });
  if (selected === q.a) score++;
  document.getElementById("quizProgress").textContent = "Question " + (currentIndex+1) + " of 10 | Score: " + score;
  if (currentIndex < 9) {
    document.getElementById("nextBtn").style.display = "inline-block";
  } else {
    showResult();
  }
}

function nextQuestion() {
  currentIndex++;
  showQuestion();
}

function showResult() {
  document.getElementById("nextBtn").style.display = "none";
  const pct = score * 10;
  const msg = pct >= 80 ? "Excellent! 🎉" : pct >= 50 ? "Good effort! Keep practising 💪" : "Needs improvement — review the topic 📚";
  document.getElementById("quizResult").innerHTML =
    "<div class=\"card\" style=\"background:#0f172a;margin-top:12px\">" +
    "<h3>Quiz Complete!</h3>" +
    "<p>Subject: " + currentSubject + " | Level: " + currentLevel + "</p>" +
    "<p style=\"font-size:24px;font-weight:700\">" + score + "/10 (" + pct + "%)</p>" +
    "<p class=\"muted\">" + msg + "</p>" +
    "<button class=\"btn\" onclick=\"document.getElementById('quizMenu').style.display='block';document.getElementById('quizBox').style.display='none'\">Back to Subjects</button>" +
    "<button class=\"btn secondary\" onclick=\"startQuiz('" + currentSubject + "','" + currentLevel + "')\">Retry</button>" +
    "</div>";
}


const QUESTIONS = {
  "Python": {
    "Beginner": [
      {q:"What is the output of print(2+3)?",o:["5","23","Error","None"],a:0},
      {q:"Which keyword defines a function in Python?",o:["func","def","function","define"],a:1},
      {q:"What data type is 3.14?",o:["int","str","float","bool"],a:2},
      {q:"How do you create a list in Python?",o:["{}","()","[]","<>"],a:2},
      {q:"What does len('hello') return?",o:["4","5","6","Error"],a:1},
      {q:"Which symbol is used for comments in Python?",o:["//","#","/*","--"],a:1},
      {q:"What is the output of type(True)?",o:["int","bool","str","NoneType"],a:1},
      {q:"How do you start a for loop in Python?",o:["for i in range:","for(i=0;i<n;i++)","for i in range(n):","loop i to n:"],a:2},
      {q:"What does print() do?",o:["Takes input","Shows output","Defines variable","None"],a:1},
      {q:"Which of these is a valid variable name?",o:["2name","my-var","my_var","class"],a:2}
    ],
    "Intermediate": [
      {q:"What is a lambda function?",o:["A class method","An anonymous function","A loop","A module"],a:1},
      {q:"What does *args do in a function?",o:["Passes keyword args","Passes variable positional args","Multiplies args","None"],a:1},
      {q:"What is list comprehension?",o:["A way to copy lists","A concise way to create lists","A sorting method","A search method"],a:1},
      {q:"What does 'self' refer to in a class?",o:["The class itself","The current instance","A method","A variable"],a:1},
      {q:"What is the output of [1,2,3][::-1]?",o:["[1,2,3]","[3,2,1]","Error","[]"],a:1},
      {q:"Which module is used for regular expressions?",o:["re","regex","regexp","match"],a:0},
      {q:"What does try/except do?",o:["Loops code","Handles errors","Defines functions","Imports modules"],a:1},
      {q:"What is a dictionary in Python?",o:["Ordered list","Key-value pairs","A set","A tuple"],a:1},
      {q:"What does 'import os' do?",o:["Imports operating system module","Creates a file","Runs a program","None"],a:0},
      {q:"What is the difference between == and is?",o:["No difference","== checks value, is checks identity","is checks value","None"],a:1}
    ],
    "Advanced": [
      {q:"What is a generator in Python?",o:["A function that returns a list","A function using yield","A class decorator","A module"],a:1},
      {q:"What is the GIL in Python?",o:["Global Import Lock","Global Interpreter Lock","General Input Loop","None"],a:1},
      {q:"What does @property decorator do?",o:["Makes a method private","Allows method to be accessed like attribute","Creates a class","None"],a:1},
      {q:"What is monkey patching?",o:["Debugging technique","Modifying code at runtime","A design pattern","None"],a:1},
      {q:"What is __slots__ used for?",o:["Memory optimisation","Error handling","Importing","None"],a:0},
      {q:"What does collections.defaultdict do?",o:["Sorts a dict","Provides default value for missing keys","Merges dicts","None"],a:1},
      {q:"What is asyncio used for?",o:["Multithreading","Asynchronous programming","Database access","None"],a:1},
      {q:"What is a metaclass?",o:["A class of a class","A base class","An abstract class","None"],a:0},
      {q:"What does functools.lru_cache do?",o:["Clears cache","Caches function results","Limits recursion","None"],a:1},
      {q:"What is the purpose of __init__.py?",o:["Runs on import","Marks directory as package","Both","None"],a:2}
    ]
  },
  "Programming Basics": {
    "Beginner": [
      {q:"What is a variable?",o:["A fixed value","A container for data","A function","A loop"],a:1},
      {q:"What is an algorithm?",o:["A programming language","A step-by-step solution","A data type","A compiler"],a:1},
      {q:"What does CPU stand for?",o:["Central Process Unit","Central Processing Unit","Computer Processing Unit","None"],a:1},
      {q:"What is a compiler?",o:["Translates code to machine language","Runs code line by line","Stores data","None"],a:0},
      {q:"What is binary?",o:["Base 10 number system","Base 2 number system","Base 16","None"],a:1},
      {q:"What is an IDE?",o:["Internet Data Exchange","Integrated Development Environment","Internal Debug Engine","None"],a:1},
      {q:"What is a loop used for?",o:["Store data","Repeat code","Define functions","None"],a:1},
      {q:"What is a boolean?",o:["A number","True or False value","A string","None"],a:1},
      {q:"What is debugging?",o:["Writing code","Finding and fixing errors","Compiling","None"],a:1},
      {q:"What is syntax?",o:["Logic of code","Rules of a programming language","A data structure","None"],a:1}
    ],
    "Intermediate": [
      {q:"What is recursion?",o:["A loop","A function calling itself","A data type","None"],a:1},
      {q:"What is OOP?",o:["Object Oriented Programming","Open Output Process","None","Online Output Program"],a:0},
      {q:"What is inheritance in OOP?",o:["Copying code","A class acquiring properties of another","A loop","None"],a:1},
      {q:"What is encapsulation?",o:["Hiding internal details","Sharing data","A loop","None"],a:0},
      {q:"What is polymorphism?",o:["Many forms of a function/class","A data type","A module","None"],a:0},
      {q:"What is a stack data structure?",o:["FIFO","LIFO","Random access","None"],a:1},
      {q:"What is a queue?",o:["LIFO","FIFO","Random","None"],a:1},
      {q:"What is Big O notation?",o:["A loop","Algorithm efficiency measurement","A data type","None"],a:1},
      {q:"What is abstraction?",o:["Hiding complexity","Showing all details","A loop","None"],a:0},
      {q:"What is a linked list?",o:["Array","Nodes connected by pointers","A queue","None"],a:1}
    ],
    "Advanced": [
      {q:"What is dynamic programming?",o:["Using dynamic variables","Solving problems by breaking into subproblems","A language","None"],a:1},
      {q:"What is a binary search tree?",o:["A tree where left < root < right","A random tree","A graph","None"],a:0},
      {q:"What is time complexity of binary search?",o:["O(n)","O(log n)","O(n2)","O(1)"],a:1},
      {q:"What is a hash table?",o:["A sorted array","Key-value store with hash function","A tree","None"],a:1},
      {q:"What is a graph in CS?",o:["A chart","Nodes connected by edges","A matrix","None"],a:1},
      {q:"What is Dijkstras algorithm used for?",o:["Sorting","Shortest path","Searching","None"],a:1},
      {q:"What is a deadlock?",o:["A bug","Two processes waiting for each other forever","A loop","None"],a:1},
      {q:"What is memoisation?",o:["Memory management","Caching results of expensive calls","Garbage collection","None"],a:1},
      {q:"What is a semaphore?",o:["A signal","Synchronisation tool for threads","A data type","None"],a:1},
      {q:"What is the difference between process and thread?",o:["No difference","Process is independent, thread shares memory","Thread is independent","None"],a:1}
    ]
  },
  "Mathematics": {
    "Beginner": [
      {q:"What is 15% of 200?",o:["25","30","35","40"],a:1},
      {q:"What is the square root of 144?",o:["10","11","12","13"],a:2},
      {q:"What is 2 to the power of 8?",o:["128","256","512","64"],a:1},
      {q:"What is the value of pi (approx)?",o:["3.14","2.71","1.61","4.13"],a:0},
      {q:"What is a prime number?",o:["Divisible by 2","Only divisible by 1 and itself","Even number","None"],a:1},
      {q:"What is the mean of 2,4,6,8,10?",o:["5","6","7","8"],a:1},
      {q:"What is 12 factorial (12!)?",o:["479001600","39916800","3628800","None"],a:0},
      {q:"What is a set in mathematics?",o:["Ordered collection","Unordered collection of unique elements","A sequence","None"],a:1},
      {q:"What is the area of a circle with radius 7?",o:["154","144","164","134"],a:0},
      {q:"What is a logarithm?",o:["Inverse of exponentiation","A type of loop","A matrix","None"],a:0}
    ],
    "Intermediate": [
      {q:"What is a matrix?",o:["A single number","A 2D array of numbers","A vector","None"],a:1},
      {q:"What is the determinant of [[1,2],[3,4]]?",o:["-2","2","-4","4"],a:0},
      {q:"What is Boolean algebra used for?",o:["Statistics","Logic circuits and CS","Calculus","None"],a:1},
      {q:"What is modular arithmetic?",o:["Division","Remainder after division","Multiplication","None"],a:1},
      {q:"What is a permutation?",o:["Ordered arrangement","Unordered selection","A set","None"],a:0},
      {q:"What is a combination?",o:["Ordered selection","Unordered selection","A sequence","None"],a:1},
      {q:"What is the Pythagorean theorem?",o:["a+b=c","a2+b2=c2","a*b=c","None"],a:1},
      {q:"What is a derivative in calculus?",o:["Area under curve","Rate of change","A constant","None"],a:1},
      {q:"What is an integral?",o:["Rate of change","Area under curve","A matrix","None"],a:1},
      {q:"What is a probability?",o:["Certainty","Likelihood of event between 0 and 1","A percentage only","None"],a:1}
    ],
    "Advanced": [
      {q:"What is Big O of bubble sort?",o:["O(n)","O(n log n)","O(n2)","O(1)"],a:2},
      {q:"What is a Fourier transform used for?",o:["Sorting","Signal analysis","Matrix multiplication","None"],a:1},
      {q:"What is linear algebra used for in ML?",o:["Storing data","Vector and matrix operations","None","Loops"],a:1},
      {q:"What is gradient descent?",o:["A sorting algorithm","Optimisation algorithm for ML","A data structure","None"],a:1},
      {q:"What is a normal distribution?",o:["Uniform spread","Bell curve distribution","Random data","None"],a:1},
      {q:"What is eigenvalue?",o:["A scalar for linear transformation","A matrix","A vector","None"],a:0},
      {q:"What is entropy in information theory?",o:["Energy","Measure of uncertainty","A constant","None"],a:1},
      {q:"What is Bayes theorem used for?",o:["Sorting","Updating probability with new evidence","Matrix ops","None"],a:1},
      {q:"What is a p-value in statistics?",o:["Probability of results given null hypothesis","A percentage","A constant","None"],a:0},
      {q:"What is the chain rule in calculus?",o:["Adding derivatives","Differentiating composite functions","Integration","None"],a:1}
    ]
  },
  "Data Structures": {
    "Beginner": [
      {q:"What is an array?",o:["Key-value store","Collection of elements in sequence","A tree","None"],a:1},
      {q:"What is a stack?",o:["FIFO structure","LIFO structure","A graph","None"],a:1},
      {q:"What is a queue?",o:["LIFO","FIFO","Random access","None"],a:1},
      {q:"What is a linked list node made of?",o:["Only data","Data and pointer to next node","Only pointer","None"],a:1},
      {q:"What is the index of first element in array?",o:["1","0","-1","None"],a:1},
      {q:"What is a tree?",o:["Linear structure","Hierarchical structure","A graph","None"],a:1},
      {q:"What is a leaf node in a tree?",o:["Root node","Node with no children","Node with two children","None"],a:1},
      {q:"What operation adds to a stack?",o:["enqueue","push","insert","add"],a:1},
      {q:"What operation removes from a stack?",o:["dequeue","pop","remove","delete"],a:1},
      {q:"What is a hash table used for?",o:["Sorting","Fast key-value lookup","Traversal","None"],a:1}
    ],
    "Intermediate": [
      {q:"What is a binary search tree?",o:["Random tree","Left < root < right","A graph","None"],a:1},
      {q:"What is time complexity of array access?",o:["O(n)","O(1)","O(log n)","None"],a:1},
      {q:"What is a heap?",o:["A stack","Tree-based structure for priority queue","A graph","None"],a:1},
      {q:"What is DFS?",o:["Depth First Search","Data File System","None","Direct File Search"],a:0},
      {q:"What is BFS?",o:["Breadth First Search","Binary File System","None","Base File Search"],a:0},
      {q:"What is a doubly linked list?",o:["Single pointer nodes","Nodes with next and prev pointers","A tree","None"],a:1},
      {q:"What is a circular queue?",o:["Queue in a circle shape","Queue where tail connects to head","A stack","None"],a:1},
      {q:"What is amortised analysis?",o:["Worst case only","Average cost over sequence of operations","Best case","None"],a:1},
      {q:"What is a trie?",o:["A graph","Tree for storing strings by prefix","A hash table","None"],a:1},
      {q:"What is a priority queue?",o:["Random queue","Queue where highest priority served first","A stack","None"],a:1}
    ],
    "Advanced": [
      {q:"What is an AVL tree?",o:["Unbalanced BST","Self-balancing BST","A heap","None"],a:1},
      {q:"What is the time complexity of heapify?",o:["O(n)","O(log n)","O(n log n)","O(1)"],a:0},
      {q:"What is a red-black tree?",o:["A coloured graph","Self-balancing BST with colour rules","A heap","None"],a:1},
      {q:"What is a segment tree used for?",o:["Sorting","Range queries on arrays","Graph traversal","None"],a:1},
      {q:"What is a Fenwick tree?",o:["A graph","Binary indexed tree for prefix sums","A heap","None"],a:1},
      {q:"What is the time complexity of merge sort?",o:["O(n2)","O(n log n)","O(n)","O(log n)"],a:1},
      {q:"What is a sparse table?",o:["Empty table","Structure for range minimum queries","A hash table","None"],a:1},
      {q:"What is topological sorting?",o:["Sorting numbers","Ordering DAG nodes by dependencies","A tree traversal","None"],a:1},
      {q:"What is a disjoint set?",o:["A graph","Union-Find data structure","A tree","None"],a:1},
      {q:"What is the time complexity of quick sort average case?",o:["O(n2)","O(n log n)","O(n)","O(log n)"],a:1}
    ]
  },
  "Networking": {
    "Beginner": [
      {q:"What does IP stand for?",o:["Internet Protocol","Internal Process","Input Port","None"],a:0},
      {q:"What is a router?",o:["Stores data","Directs network traffic","Displays web pages","None"],a:1},
      {q:"What does HTTP stand for?",o:["HyperText Transfer Protocol","High Transfer Protocol","None","Host Transfer Process"],a:0},
      {q:"What is a MAC address?",o:["Software address","Hardware address of network interface","IP address","None"],a:1},
      {q:"What does DNS stand for?",o:["Domain Name System","Data Network Service","None","Direct Name Server"],a:0},
      {q:"What is a firewall?",o:["A physical wall","Security system filtering network traffic","A router","None"],a:1},
      {q:"What is bandwidth?",o:["Speed of CPU","Data transfer capacity of network","Memory size","None"],a:1},
      {q:"What is Wi-Fi?",o:["Wired connection","Wireless network technology","A protocol","None"],a:1},
      {q:"What is a server?",o:["A client machine","Computer providing services to other computers","A router","None"],a:1},
      {q:"What is a packet?",o:["A physical package","Unit of data in a network","A protocol","None"],a:1}
    ],
    "Intermediate": [
      {q:"What is TCP vs UDP?",o:["Both reliable","TCP reliable, UDP faster but unreliable","UDP reliable","None"],a:1},
      {q:"What is the OSI model?",o:["A protocol","7-layer network communication framework","A hardware standard","None"],a:1},
      {q:"What is subnetting?",o:["Connecting networks","Dividing network into smaller sub-networks","A protocol","None"],a:1},
      {q:"What is DHCP?",o:["Dynamic Host Configuration Protocol","Direct Host Control","None","Data Host Connection"],a:0},
      {q:"What is a VPN?",o:["Virtual Private Network","Very Private Node","None","Virtual Public Network"],a:0},
      {q:"What is ARP?",o:["Address Resolution Protocol","Auto Routing Protocol","None","Automatic Request Protocol"],a:0},
      {q:"What is a socket?",o:["A hardware port","Endpoint for network communication","A protocol","None"],a:1},
      {q:"What is NAT?",o:["Network Address Translation","Node Access Table","None","Network Automation Tool"],a:0},
      {q:"What is latency?",o:["Bandwidth","Delay in data transmission","Speed","None"],a:1},
      {q:"What is a proxy server?",o:["A firewall","Intermediary between client and server","A router","None"],a:1}
    ],
    "Advanced": [
      {q:"What is BGP?",o:["Border Gateway Protocol","Basic Graph Protocol","None","Binary Gateway Process"],a:0},
      {q:"What is OSPF?",o:["Open Shortest Path First","Optional Secure Protocol","None","Output Signal Path"],a:0},
      {q:"What is a VLAN?",o:["Virtual LAN","Very Large Area Network","None","Virtual Link Access Node"],a:0},
      {q:"What is SSL/TLS used for?",o:["Routing","Encrypting network communication","Compression","None"],a:1},
      {q:"What is a CDN?",o:["Content Delivery Network","Central Data Node","None","Core Distribution Network"],a:0},
      {q:"What is QoS?",o:["Quality of Service","Queue of Servers","None","Query on System"],a:0},
      {q:"What is MPLS?",o:["Multi Protocol Label Switching","Main Protocol Layer","None","Multi Path Local Switch"],a:0},
      {q:"What is a zero-day vulnerability?",o:["A known bug","Unknown vulnerability with no patch","A firewall rule","None"],a:1},
      {q:"What is anycast routing?",o:["Broadcasting","Routing to nearest node in a group","Multicasting","None"],a:1},
      {q:"What is a SYN flood attack?",o:["A virus","DDoS attack exploiting TCP handshake","A worm","None"],a:1}
    ]
  },
  "Database": {
    "Beginner": [
      {q:"What does SQL stand for?",o:["Structured Query Language","Simple Query Logic","None","System Query Layer"],a:0},
      {q:"What is a primary key?",o:["Any column","Unique identifier for a row","A foreign key","None"],a:1},
      {q:"What does SELECT do in SQL?",o:["Deletes data","Retrieves data","Updates data","None"],a:1},
      {q:"What is a table in a database?",o:["A chart","Organised rows and columns of data","A query","None"],a:1},
      {q:"What does INSERT do?",o:["Updates rows","Adds new rows","Deletes rows","None"],a:1},
      {q:"What does DELETE do?",o:["Updates rows","Adds rows","Removes rows","None"],a:2},
      {q:"What is a foreign key?",o:["A primary key","References primary key of another table","A unique key","None"],a:1},
      {q:"What does WHERE clause do?",o:["Sorts data","Filters rows based on condition","Groups data","None"],a:1},
      {q:"What is NULL in SQL?",o:["Zero","Empty string","Missing or unknown value","None"],a:2},
      {q:"What does ORDER BY do?",o:["Filters","Sorts results","Groups","None"],a:1}
    ],
    "Intermediate": [
      {q:"What is a JOIN in SQL?",o:["Splits tables","Combines rows from multiple tables","Deletes tables","None"],a:1},
      {q:"What is normalisation?",o:["Making database faster","Organising to reduce redundancy","Backing up","None"],a:1},
      {q:"What is an index in a database?",o:["A primary key","Structure to speed up queries","A table","None"],a:1},
      {q:"What is ACID?",o:["A chemical","Atomicity, Consistency, Isolation, Durability","A protocol","None"],a:1},
      {q:"What is a stored procedure?",o:["A table","Saved SQL code that can be executed","A view","None"],a:1},
      {q:"What is a view in SQL?",o:["A table copy","Virtual table based on a query","A stored procedure","None"],a:1},
      {q:"What does GROUP BY do?",o:["Sorts data","Groups rows sharing a value","Filters data","None"],a:1},
      {q:"What is a transaction?",o:["A query","Unit of work that is all-or-nothing","A table","None"],a:1},
      {q:"What is referential integrity?",o:["Data accuracy","Foreign key always refers to valid primary key","None","Backup"],a:1},
      {q:"What is the difference between INNER and LEFT JOIN?",o:["No difference","INNER returns matches only, LEFT returns all left rows","None","RIGHT returns all"],a:1}
    ],
    "Advanced": [
      {q:"What is query optimisation?",o:["Writing longer queries","Improving query performance","Normalisation","None"],a:1},
      {q:"What is a clustered index?",o:["Non-unique index","Index that sorts and stores data rows","A foreign key","None"],a:1},
      {q:"What is sharding?",o:["Backing up","Splitting database across multiple machines","Normalisation","None"],a:1},
      {q:"What is CAP theorem?",o:["A sorting algorithm","Consistency, Availability, Partition tolerance tradeoff","A protocol","None"],a:1},
      {q:"What is a NoSQL database?",o:["A bad database","Non-relational database","SQL without joins","None"],a:1},
      {q:"What is database replication?",o:["Deleting copies","Copying database to multiple servers","Normalisation","None"],a:1},
      {q:"What is an ORM?",o:["A query language","Object Relational Mapper","A database type","None"],a:1},
      {q:"What is eventual consistency?",o:["Immediate consistency","System will become consistent over time","ACID property","None"],a:1},
      {q:"What is a materialized view?",o:["A virtual table","Stored result of a query updated periodically","A stored procedure","None"],a:1},
      {q:"What is connection pooling?",o:["Network setting","Reusing database connections for efficiency","A join type","None"],a:1}
    ]
  }
};

let currentSubject = "", currentLevel = "", currentIndex = 0, score = 0, answered = false;

function startQuiz(subject, level) {
  currentSubject = subject;
  currentLevel = level;
  currentIndex = 0;
  score = 0;
  answered = false;
  document.getElementById("quizMenu").style.display = "none";
  document.getElementById("quizBox").style.display = "block";
  document.getElementById("quizResult").innerHTML = "";
  showQuestion();
}

function showQuestion() {
  const qs = QUESTIONS[currentSubject][currentLevel];
  const q = qs[currentIndex];
  answered = false;
  document.getElementById("quizTitle").textContent = currentSubject + " — " + currentLevel;
  document.getElementById("quizProgress").textContent = "Question " + (currentIndex+1) + " of 10 | Score: " + score;
  document.getElementById("quizQuestion").innerHTML = "<p style=\"font-size:16px;margin:0\">" + q.q + "</p>";
  document.getElementById("nextBtn").style.display = "none";
  const opts = document.getElementById("quizOptions");
  opts.innerHTML = q.o.map((opt, i) =>
    "<button class=\"btn\" style=\"display:block;width:100%;margin-bottom:8px;text-align:left;background:rgba(15,23,42,0.9);border:1px solid #334155\" onclick=\"checkAnswer(" + i + ")\">" + opt + "</button>"
  ).join("");
}

function checkAnswer(selected) {
  if (answered) return;
  answered = true;
  const qs = QUESTIONS[currentSubject][currentLevel];
  const q = qs[currentIndex];
  const btns = document.getElementById("quizOptions").querySelectorAll("button");
  btns.forEach((btn, i) => {
    btn.disabled = true;
    if (i === q.a) btn.style.background = "linear-gradient(135deg,#166534,#15803d)";
    else if (i === selected && selected !== q.a) btn.style.background = "linear-gradient(135deg,#7f1d1d,#991b1b)";
  });
  if (selected === q.a) score++;
  document.getElementById("quizProgress").textContent = "Question " + (currentIndex+1) + " of 10 | Score: " + score;
  if (currentIndex < 9) {
    document.getElementById("nextBtn").style.display = "inline-block";
  } else {
    showResult();
  }
}

function nextQuestion() {
  currentIndex++;
  showQuestion();
}

function showResult() {
  document.getElementById("nextBtn").style.display = "none";
  const pct = score * 10;
  const msg = pct >= 80 ? "Excellent! 🎉" : pct >= 50 ? "Good effort! Keep practising 💪" : "Needs improvement — review the topic 📚";
  document.getElementById("quizResult").innerHTML =
    "<div class=\"card\" style=\"background:#0f172a;margin-top:12px\">" +
    "<h3>Quiz Complete!</h3>" +
    "<p>Subject: " + currentSubject + " | Level: " + currentLevel + "</p>" +
    "<p style=\"font-size:24px;font-weight:700\">" + score + "/10 (" + pct + "%)</p>" +
    "<p class=\"muted\">" + msg + "</p>" +
    "<button class=\"btn\" onclick=\"document.getElementById('quizMenu').style.display='block';document.getElementById('quizBox').style.display='none'\">Back to Subjects</button>" +
    "<button class=\"btn secondary\" onclick=\"startQuiz('" + currentSubject + "','" + currentLevel + "')\">Retry</button>" +
    "</div>";
}


var QS={
  Python:{
    Beginner:[
      {q:"What is output of print(2+3)?",o:["5","23","Error","None"],a:0},
      {q:"Which keyword defines a function?",o:["func","def","function","define"],a:1},
      {q:"What type is 3.14?",o:["int","str","float","bool"],a:2},
      {q:"How to create a list?",o:["{}","()","[]","<>"],a:2},
      {q:"What does len('hello') return?",o:["4","5","6","Error"],a:1},
      {q:"Comment symbol in Python?",o:["//","#","/*","--"],a:1},
      {q:"Output of type(True)?",o:["int","bool","str","NoneType"],a:1},
      {q:"Valid variable name?",o:["2name","my-var","my_var","class"],a:2},
      {q:"What does print() do?",o:["Input","Output","Define var","None"],a:1},
      {q:"How to start a for loop?",o:["for i in range:","for(i=0;;)","for i in range(n):","loop i:"],a:2}
    ],
    Intermediate:[
      {q:"What is a lambda?",o:["Class method","Anonymous function","A loop","A module"],a:1},
      {q:"What does *args do?",o:["Keyword args","Variable positional args","Multiply","None"],a:1},
      {q:"What is list comprehension?",o:["Copy lists","Create lists concisely","Sort","Search"],a:1},
      {q:"What does self refer to?",o:["The class","Current instance","A method","A var"],a:1},
      {q:"Output of [1,2,3][::-1]?",o:["[1,2,3]","[3,2,1]","Error","[]"],a:1},
      {q:"Module for regex?",o:["re","regex","regexp","match"],a:0},
      {q:"What does try/except do?",o:["Loop","Handle errors","Define func","Import"],a:1},
      {q:"What is a dictionary?",o:["Ordered list","Key-value pairs","A set","A tuple"],a:1},
      {q:"What does import os do?",o:["OS module","Create file","Run program","None"],a:0},
      {q:"== vs is in Python?",o:["Same","== value, is identity","is value","None"],a:1}
    ],
    Advanced:[
      {q:"What is a generator?",o:["Returns list","Uses yield","Class decorator","Module"],a:1},
      {q:"What is GIL?",o:["Global Import Lock","Global Interpreter Lock","General Input","None"],a:1},
      {q:"What does @property do?",o:["Private method","Access method like attribute","Create class","None"],a:1},
      {q:"What is monkey patching?",o:["Debugging","Modify code at runtime","Design pattern","None"],a:1},
      {q:"What is __slots__?",o:["Memory optimisation","Error handling","Importing","None"],a:0},
      {q:"What is defaultdict?",o:["Sort dict","Default for missing keys","Merge dicts","None"],a:1},
      {q:"What is asyncio?",o:["Multithreading","Async programming","DB access","None"],a:1},
      {q:"What is a metaclass?",o:["Class of class","Base class","Abstract class","None"],a:0},
      {q:"What does lru_cache do?",o:["Clear cache","Cache results","Limit recursion","None"],a:1},
      {q:"Purpose of __init__.py?",o:["Run on import","Mark as package","Both","None"],a:2}
    ]
  },
  Basics:{
    Beginner:[
      {q:"What is a variable?",o:["Fixed value","Data container","A function","A loop"],a:1},
      {q:"What is an algorithm?",o:["A language","Step-by-step solution","A data type","A compiler"],a:1},
      {q:"What does CPU stand for?",o:["Central Process Unit","Central Processing Unit","Computer Processing","None"],a:1},
      {q:"What is a compiler?",o:["Translates to machine code","Runs line by line","Stores data","None"],a:0},
      {q:"What is binary?",o:["Base 10","Base 2","Base 16","None"],a:1},
      {q:"What is an IDE?",o:["Internet Data Exchange","Integrated Dev Environment","Internal Debug","None"],a:1},
      {q:"What is a loop?",o:["Store data","Repeat code","Define functions","None"],a:1},
      {q:"What is a boolean?",o:["A number","True or False","A string","None"],a:1},
      {q:"What is debugging?",o:["Writing code","Finding and fixing errors","Compiling","None"],a:1},
      {q:"What is syntax?",o:["Logic of code","Rules of a language","A structure","None"],a:1}
    ],
    Intermediate:[
      {q:"What is recursion?",o:["A loop","Function calling itself","A data type","None"],a:1},
      {q:"What is OOP?",o:["Object Oriented Programming","Open Output Process","None","Online Output"],a:0},
      {q:"What is inheritance?",o:["Copying code","Class acquiring properties of another","A loop","None"],a:1},
      {q:"What is encapsulation?",o:["Hiding internal details","Sharing data","A loop","None"],a:0},
      {q:"What is polymorphism?",o:["Many forms","A data type","A module","None"],a:0},
      {q:"What is a stack?",o:["FIFO","LIFO","Random access","None"],a:1},
      {q:"What is a queue?",o:["LIFO","FIFO","Random","None"],a:1},
      {q:"What is Big O?",o:["A loop","Algorithm efficiency","A data type","None"],a:1},
      {q:"What is abstraction?",o:["Hiding complexity","Showing all details","A loop","None"],a:0},
      {q:"What is a linked list?",o:["Array","Nodes with pointers","A queue","None"],a:1}
    ],
    Advanced:[
      {q:"What is dynamic programming?",o:["Dynamic variables","Solving by subproblems","A language","None"],a:1},
      {q:"What is a BST?",o:["Left < root < right","Random tree","A graph","None"],a:0},
      {q:"Time complexity of binary search?",o:["O(n)","O(log n)","O(n2)","O(1)"],a:1},
      {q:"What is a hash table?",o:["Sorted array","Key-value with hash","A tree","None"],a:1},
      {q:"What is a graph?",o:["A chart","Nodes connected by edges","A matrix","None"],a:1},
      {q:"What is Dijkstra used for?",o:["Sorting","Shortest path","Searching","None"],a:1},
      {q:"What is a deadlock?",o:["A bug","Two processes waiting forever","A loop","None"],a:1},
      {q:"What is memoisation?",o:["Memory management","Caching expensive calls","Garbage collection","None"],a:1},
      {q:"What is a semaphore?",o:["A signal","Thread sync tool","A data type","None"],a:1},
      {q:"Process vs thread?",o:["No difference","Process independent, thread shares memory","Thread independent","None"],a:1}
    ]
  },
  Math:{
    Beginner:[
      {q:"What is 15% of 200?",o:["25","30","35","40"],a:1},
      {q:"Square root of 144?",o:["10","11","12","13"],a:2},
      {q:"2 to the power of 8?",o:["128","256","512","64"],a:1},
      {q:"Value of pi?",o:["3.14","2.71","1.61","4.13"],a:0},
      {q:"What is a prime number?",o:["Divisible by 2","Only by 1 and itself","Even number","None"],a:1},
      {q:"Mean of 2,4,6,8,10?",o:["5","6","7","8"],a:1},
      {q:"What is a set?",o:["Ordered collection","Unique unordered elements","A sequence","None"],a:1},
      {q:"Area of circle r=7?",o:["154","144","164","134"],a:0},
      {q:"What is a logarithm?",o:["Inverse of exponentiation","A loop","A matrix","None"],a:0},
      {q:"What is factorial?",o:["Sum of numbers","Product of all integers up to n","A power","None"],a:1}
    ],
    Intermediate:[
      {q:"What is a matrix?",o:["Single number","2D array of numbers","A vector","None"],a:1},
      {q:"Determinant of [[1,2],[3,4]]?",o:["-2","2","-4","4"],a:0},
      {q:"Boolean algebra used for?",o:["Statistics","Logic circuits","Calculus","None"],a:1},
      {q:"What is modular arithmetic?",o:["Division","Remainder after division","Multiplication","None"],a:1},
      {q:"What is a permutation?",o:["Ordered arrangement","Unordered selection","A set","None"],a:0},
      {q:"What is a combination?",o:["Ordered selection","Unordered selection","A sequence","None"],a:1},
      {q:"Pythagorean theorem?",o:["a+b=c","a2+b2=c2","a*b=c","None"],a:1},
      {q:"What is a derivative?",o:["Area under curve","Rate of change","A constant","None"],a:1},
      {q:"What is an integral?",o:["Rate of change","Area under curve","A matrix","None"],a:1},
      {q:"What is probability?",o:["Certainty","Likelihood between 0 and 1","Percentage only","None"],a:1}
    ],
    Advanced:[
      {q:"Big O of bubble sort?",o:["O(n)","O(n log n)","O(n2)","O(1)"],a:2},
      {q:"Fourier transform used for?",o:["Sorting","Signal analysis","Matrix multiply","None"],a:1},
      {q:"Linear algebra in ML?",o:["Storing data","Vector and matrix ops","None","Loops"],a:1},
      {q:"What is gradient descent?",o:["Sorting algorithm","ML optimisation","A structure","None"],a:1},
      {q:"What is normal distribution?",o:["Uniform spread","Bell curve","Random data","None"],a:1},
      {q:"What is eigenvalue?",o:["Scalar for linear transform","A matrix","A vector","None"],a:0},
      {q:"What is entropy?",o:["Energy","Measure of uncertainty","A constant","None"],a:1},
      {q:"What is Bayes theorem?",o:["Sorting","Update probability with evidence","Matrix ops","None"],a:1},
      {q:"What is a p-value?",o:["Probability given null hypothesis","A percentage","A constant","None"],a:0},
      {q:"What is chain rule?",o:["Adding derivatives","Differentiating composites","Integration","None"],a:1}
    ]
  },
  DSA:{
    Beginner:[
      {q:"What is an array?",o:["Key-value store","Sequential elements","A tree","None"],a:1},
      {q:"What is a stack?",o:["FIFO","LIFO","A graph","None"],a:1},
      {q:"What is a queue?",o:["LIFO","FIFO","Random access","None"],a:1},
      {q:"Linked list node contains?",o:["Only data","Data and next pointer","Only pointer","None"],a:1},
      {q:"Index of first array element?",o:["1","0","-1","None"],a:1},
      {q:"What is a tree?",o:["Linear structure","Hierarchical structure","A graph","None"],a:1},
      {q:"What is a leaf node?",o:["Root node","No children node","Two children node","None"],a:1},
      {q:"Operation to add to stack?",o:["enqueue","push","insert","add"],a:1},
      {q:"Operation to remove from stack?",o:["dequeue","pop","remove","delete"],a:1},
      {q:"Hash table used for?",o:["Sorting","Fast key-value lookup","Traversal","None"],a:1}
    ],
    Intermediate:[
      {q:"What is a BST?",o:["Random tree","Left < root < right","A graph","None"],a:1},
      {q:"Time complexity of array access?",o:["O(n)","O(1)","O(log n)","None"],a:1},
      {q:"What is a heap?",o:["A stack","Priority queue tree","A graph","None"],a:1},
      {q:"What is DFS?",o:["Depth First Search","Data File System","None","Direct File Search"],a:0},
      {q:"What is BFS?",o:["Breadth First Search","Binary File System","None","Base File Search"],a:0},
      {q:"What is doubly linked list?",o:["Single pointer","Next and prev pointers","A tree","None"],a:1},
      {q:"What is circular queue?",o:["Circle shape","Tail connects to head","A stack","None"],a:1},
      {q:"What is amortised analysis?",o:["Worst case","Average over operations","Best case","None"],a:1},
      {q:"What is a trie?",o:["A graph","String prefix tree","A hash table","None"],a:1},
      {q:"What is priority queue?",o:["Random","Highest priority first","A stack","None"],a:1}
    ],
    Advanced:[
      {q:"What is an AVL tree?",o:["Unbalanced BST","Self-balancing BST","A heap","None"],a:1},
      {q:"Time complexity of heapify?",o:["O(n)","O(log n)","O(n log n)","O(1)"],a:0},
      {q:"What is a red-black tree?",o:["Coloured graph","Self-balancing BST with colour rules","A heap","None"],a:1},
      {q:"Segment tree used for?",o:["Sorting","Range queries","Graph traversal","None"],a:1},
      {q:"What is a Fenwick tree?",o:["A graph","Binary indexed tree","A heap","None"],a:1},
      {q:"Time complexity of merge sort?",o:["O(n2)","O(n log n)","O(n)","O(log n)"],a:1},
      {q:"What is topological sorting?",o:["Sorting numbers","Ordering DAG by dependencies","Tree traversal","None"],a:1},
      {q:"What is disjoint set?",o:["A graph","Union-Find structure","A tree","None"],a:1},
      {q:"Quick sort average case?",o:["O(n2)","O(n log n)","O(n)","O(log n)"],a:1},
      {q:"What is a sparse table?",o:["Empty table","Range minimum queries","A hash table","None"],a:1}
    ]
  }
};

var curSubject="",curLevel="",curIdx=0,curScore=0,curAnswered=false;

function startQuiz(s,l){
  curSubject=s;curLevel=l;curIdx=0;curScore=0;curAnswered=false;
  document.getElementById("quizMenu").style.display="none";
  document.getElementById("quizBox").style.display="block";
  document.getElementById("quizResult").innerHTML="";
  showQ();
}

function showQ(){
  var q=QS[curSubject][curLevel][curIdx];
  curAnswered=false;
  document.getElementById("quizTitle").textContent=curSubject+" — "+curLevel;
  document.getElementById("quizProgress").textContent="Question "+(curIdx+1)+" of 10 | Score: "+curScore;
  document.getElementById("quizQuestion").innerHTML="<p style='font-size:16px;margin:0'>"+q.q+"</p>";
  document.getElementById("nextBtn").style.display="none";
  document.getElementById("quizOptions").innerHTML=q.o.map(function(opt,i){
    return "<button class='btn' style='display:block;width:100%;margin-bottom:8px;text-align:left;background:rgba(15,23,42,0.9);border:1px solid #334155' onclick='checkA("+i+")'>"+opt+"</button>";
  }).join("");
}

function checkA(sel){
  if(curAnswered)return;
  curAnswered=true;
  var q=QS[curSubject][curLevel][curIdx];
  var btns=document.getElementById("quizOptions").querySelectorAll("button");
  btns.forEach(function(btn,i){
    btn.disabled=true;
    if(i===q.a)btn.style.background="linear-gradient(135deg,#166534,#15803d)";
    else if(i===sel&&sel!==q.a)btn.style.background="linear-gradient(135deg,#7f1d1d,#991b1b)";
  });
  if(sel===q.a)curScore++;
  document.getElementById("quizProgress").textContent="Question "+(curIdx+1)+" of 10 | Score: "+curScore;
  if(curIdx<9){document.getElementById("nextBtn").style.display="inline-block";}
  else{showRes();}
}

function nextQuestion(){curIdx++;showQ();}

function showRes(){
  document.getElementById("nextBtn").style.display="none";
  var pct=curScore*10;
  var msg=pct>=80?"Excellent! You are ready!":pct>=50?"Good effort! Keep practising!":"Needs improvement — review the topic!";
  document.getElementById("quizResult").innerHTML=
    "<div class='card' style='background:#0f172a;margin-top:12px'>"+
    "<h3>Quiz Complete!</h3>"+
    "<p>"+curSubject+" | "+curLevel+"</p>"+
    "<p style='font-size:28px;font-weight:700'>"+curScore+"/10 ("+pct+"%)</p>"+
    "<p class='muted'>"+msg+"</p>"+
    "<button class='btn' onclick='document.getElementById("quizMenu").style.display="block";document.getElementById("quizBox").style.display="none"'>Back to Subjects</button> "+
    "<button class='btn secondary' onclick='startQuiz(""+curSubject+"",""+curLevel+"")'>Retry</button>"+
    "</div>";
}

fetch("/api/analytics").then(r=>r.json()).then(data=>{document.getElementById("analyticsBox").innerHTML="<div class=\"mini\"><div class=\"tag\">Sessions</div><div>"+data.sessions+"</div></div><div class=\"mini\"><div class=\"tag\">Questions</div><div>"+data.questions+"</div></div><div class=\"mini\"><div class=\"tag\">Weak Topics</div><div>"+data.topics+"</div></div>";});
</script>
</body></html>
"""


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.get("/api/health")
def health():
    q = sum(1 for _ in DATA_FILE.open("r", encoding="utf-8")) if DATA_FILE.exists() else 0
    return jsonify({"status": "ok", "questions": q, "azure_openai": OPENAI_OK, "azure_language": LANGUAGE_OK})

@app.post("/start")
def start():
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "General Knowledge").strip()
    level = (data.get("level") or "Beginner").strip()
    count = int(data.get("count") or 10)
    questions = generate_quiz_questions(topic, level=level, count=count)
    return jsonify({"topic": topic, "level": level, "questions": questions})

@app.post("/answer")
def answer():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", [])
    questions = data.get("questions", [])
    username = data.get("username")
    topic = data.get("topic", "")
    level = data.get("level", "")
    score = sum(1 for q, a in zip(questions, answers) if a == q.get("answer"))
    feedback = analyze_answers(answers)
    if username:
        users = _load_users()
        user = users.get(username)
        if user is not None:
            user.setdefault("tests", []).append({
                "topic": topic,
                "level": level,
                "score": score,
                "max_score": len(questions),
                "date": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "feedback": feedback,
            })
            _save_users(users)
    return jsonify({"score": score, "feedback": feedback, "answers": answers})

@app.post("/api/signup")
def signup():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    if _get_user(username):
        return jsonify({"error": "Username already exists."}), 400
    user = _create_user(username, password)
    return jsonify({"username": user["username"], "tests": user["tests"], "message": "Account created."})

@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    user = _get_user(username)
    if not user or user.get("password") != password:
        return jsonify({"error": "Invalid username or password."}), 401
    return jsonify({"username": user["username"], "tests": user.get("tests", [])})

@app.get("/api/dashboard")
def dashboard():
    username = request.args.get("username", "").strip()
    user = _get_user(username)
    if not user:
        return jsonify({"error": "User not found."}), 404
    tests = user.get("tests", [])
    attempted = len(tests)
    average = 0
    if attempted:
        average = round(sum((t.get("score", 0) / max(1, t.get("max_score", 1))) * 100 for t in tests) / attempted, 1)
    return jsonify({
        "username": username,
        "attempted": attempted,
        "average": average,
        "study_percentage": average,
        "recent_tests": tests[-5:],
        "planner": {
            "recommended_focus": "Review weak topics from your last quizzes and practice more questions.",
            "next_step": "Try another quiz on a subject you missed.",
        },
    })

@app.get("/api/demo")
def demo():
    return jsonify({"message": "Adaptive mode ready: revisit loops, functions, and reasoning before next quiz.", "focus": "Python basics + problem solving", "difficulty": "medium", "source": "fallback"})

@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", [])
    text = " ".join(answers).lower()
    detected = [k for k in ["recursion","loop","function","variable","array","class","algorithm","mathematics","sorting"] if k in text]
    advice = f"Review these topics: {', '.join(detected)}." if detected else "Keep practising regularly."
    return jsonify({"weak_topics": detected, "advice": advice, "source": "fallback"})

@app.post("/api/study-plan")
def study_plan():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Please provide a prompt for the AI study coach."}), 400

    keywords = [
        "python", "loops", "functions", "recursion", "arrays", "classes", "oop",
        "algorithms", "data structures", "sorting", "math", "database", "security",
    ]
    found = [k for k in keywords if k in prompt.lower()]
    if not found:
        found = ["general IT study topics"]

    plan_topics = ", ".join(found)
    study_plan_text = (
        f"AI Study Plan for {plan_topics}:\n"
        "1. Review the core concepts and definitions.\n"
        "2. Practice 5 targeted questions for each topic.\n"
        "3. Write a short summary of mistakes.\n"
        "4. Repeat the hardest topic tomorrow.\n"
        "5. Use quick examples to build confidence."
    )
    response_text = (
        f"Here is a study plan focused on {plan_topics}.\n" + study_plan_text
        if "plan" in prompt.lower() or "study" in prompt.lower()
        else f"I can help you practice {plan_topics}. Ask me for a summary, quiz tips, or a review plan."
    )
    advice = "Focus on one topic at a time and review short examples."
    return jsonify({
        "response": response_text,
        "study_plan": study_plan_text,
        "advice": advice,
        "source": "fallback",
    })

@app.get("/api/analytics")
def analytics():
    question_count = sum(1 for _ in DATA_FILE.open("r", encoding="utf-8")) if DATA_FILE.exists() else 0
    history_lines = [l.strip() for l in HISTORY_FILE.open("r", encoding="utf-8") if l.strip()] if HISTORY_FILE.exists() else []
    results_lines = [l.strip() for l in RESULTS_FILE.open("r", encoding="utf-8") if l.strip()] if RESULTS_FILE.exists() else []
    return jsonify({"sessions": len(history_lines) + len(results_lines), "questions": question_count, "topics": "Python, Loops, Functions"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
