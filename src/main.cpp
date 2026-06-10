#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <algorithm>
#include <map>
#ifdef _WIN32
#include <conio.h>
#else
#include <termios.h>
#include <unistd.h>
#endif
#include <chrono>
#include <thread>
#include <iomanip>
#include <limits>
#include <cctype>


using namespace std;

class Question;

void clearScreen()
{
    cout << "\033[2J\033[H";
    cout.flush();
}

string generateAiRoadmap(const string &studentName, const vector<string> &weakTopics)
{
    string roadmap = "  Offline study roadmap for " + studentName + ":\n";
    if (weakTopics.empty())
    {
        roadmap += "  - Review mixed practice questions and revisit your notes.\n";
        roadmap += "  - Solve 5 short quizzes on different topics to build confidence.\n";
        roadmap += "  - Keep a small mistake log and review it every week.\n";
        roadmap += "  - Stay consistent: 15 minutes of revision daily beats cramming.\n";
        return roadmap;
    }

    for (const string &topic : weakTopics)
    {
        roadmap += "  - Review " + topic + " with 3 practice questions and one short summary note.\n";
    }
    roadmap += "  - Reattempt the same quiz tomorrow to confirm improvement.\n";
    roadmap += "  - Keep practicing calmly; small daily steps lead to strong results.\n";
    return roadmap;
}

string toLowerCopy(string text)
{
    transform(text.begin(), text.end(), text.begin(), [](unsigned char c)
              { return static_cast<char>(tolower(c)); });
    return text;
}

string extractAiText(const string &body)
{
    size_t contentPos = body.find("\"content\":\"");
    if (contentPos == string::npos)
        return "";

    contentPos += 12;
    string content;
    for (size_t i = contentPos; i < body.size(); ++i)
    {
        if (body[i] == '\\' && i + 1 < body.size())
        {
            if (body[i + 1] == 'n') content += '\n';
            else if (body[i + 1] == 't') content += '\t';
            else if (body[i + 1] == '"') content += '"';
            else if (body[i + 1] == '\\') content += '\\';
            else content += body[i + 1];
            ++i;
        }
        else if (body[i] == '"')
        {
            break;
        }
        else
        {
            content += body[i];
        }
    }
    return content;
}




  
 


string getMaskedPassword(const string &prompt = "  Password: ")
{
#ifdef _WIN32
    cout << prompt;
    cout.flush();

    string password;
    char ch;

    while (true)
    {
        ch = _getch();

        if (ch == 13)
        {
            cout << '\n';
            break;
        }
        else if (ch == 8 || ch == 127)
        {
            if (!password.empty())
            {
                password.pop_back();
                cout << "\b \b";
                cout.flush();
            }
        }
        else
        {
            password.push_back(ch);
            cout << '*';
            cout.flush();
        }
    }

    return password;
#else
    struct termios oldt, newt;
    string password;

    if (tcgetattr(STDIN_FILENO, &oldt) == 0)
    {
        newt = oldt;
        newt.c_lflag &= static_cast<unsigned int>(~ECHO);
        if (tcsetattr(STDIN_FILENO, TCSANOW, &newt) == 0)
        {
            cout << prompt;
            cout.flush();

            char ch;
            while (cin.get(ch) && ch != '\n' && ch != '\r')
            {
                if (ch == 127 || ch == 8)
                {
                    if (!password.empty())
                    {
                        password.pop_back();
                        cout << "\b \b";
                        cout.flush();
                    }
                }
                else
                {
                    password.push_back(ch);
                    cout << '*';
                    cout.flush();
                }
            }

            cout << '\n';
            tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
            return password;
        }
    }

    cout << prompt;
    cout.flush();
    getline(cin, password);
    return password;
#endif
}

bool isStrongPassword(const string &password)
{
    if (password.length() < 8)
        return false;

    bool hasLetter = false;
    bool hasDigit = false;
    bool hasSpecial = false;

    for (unsigned char ch : password)
    {
        if (isalpha(ch))
            hasLetter = true;
        else if (isdigit(ch))
            hasDigit = true;
        else
            hasSpecial = true;
    }

    return hasLetter && hasDigit && hasSpecial;
}

class Question
{
public:
    string text, optA, optB, optC, optD, answer, hint, difficulty;

    Question(string t, string a, string b, string c, string d, string ans, string h = "", string diff = "Mixed")
    {
        text = t;
        optA = a;
        optB = b;
        optC = c;
        optD = d;
        answer = ans;
        hint = h;
        difficulty = diff.empty() ? "Mixed" : diff;
    }

    void show()
    {
        cout << "\n+--------------------------------------------------+" << endl;
        cout << "|  Q: " << text << "";
        for (size_t i = text.length(); i < 48; ++i) cout << ' ';
        cout << "|" << endl;
        cout << "+--------------------------------------------------+" << endl;
        cout << "|  A) " << optA;
        for (size_t i = optA.length(); i < 46; ++i) cout << ' ';
        cout << "|" << endl;
        cout << "|  B) " << optB;
        for (size_t i = optB.length(); i < 46; ++i) cout << ' ';
        cout << "|" << endl;
        cout << "|  C) " << optC;
        for (size_t i = optC.length(); i < 46; ++i) cout << ' ';
        cout << "|" << endl;
        cout << "|  D) " << optD;
        for (size_t i = optD.length(); i < 46; ++i) cout << ' ';
        cout << "|" << endl;
        if (!difficulty.empty())
        {
            cout << "|  Difficulty: " << difficulty;
            for (size_t i = difficulty.length() + 13; i < 47; ++i) cout << ' ';
            cout << "|" << endl;
        }
        if (!hint.empty())
        {
            cout << "|  Hint: " << hint;
            for (size_t i = hint.length() + 8; i < 47; ++i) cout << ' ';
            cout << "|" << endl;
        }
        cout << "+--------------------------------------------------+" << endl;
    }
};

string generateAiHint(const Question *q)
{
    if (!q) return "  [Offline] No question data available.";

    if (!q->hint.empty())
        return "  [Offline Hint] " + q->hint;

    string hint = "  [Offline Hint] Check the wording carefully and eliminate the options that do not fit the question statement.";
    if (q->optA.find("true") != string::npos || q->optA.find("false") != string::npos)
        hint += " Look for the strongest factual statement.";
    return hint;
}

class DiagnosticAgent
{
public:
    int totalQuestions = 0;
    int correctAnswers = 0;
    int wrongAnswers = 0;
    int hintsUsed = 0;
    long long totalResponseMs = 0;
    map<string, int> incorrectCategoryFrequency;

    void recordAnswer(long long responseMs, bool isCorrect, const string &topic, bool usedHint)
    {
        ++totalQuestions;
        totalResponseMs += responseMs;
        if (isCorrect) ++correctAnswers; else ++wrongAnswers;
        if (usedHint) ++hintsUsed;
        if (!topic.empty() && !isCorrect)
            incorrectCategoryFrequency[topic]++;
    }

    void printSummary(const string &name)
    {
        cout << "\n╔══════════════════════════════════════════════════════╗" << endl;
        cout << "║            DIAGNOSTIC AGENT ANALYTICS               ║" << endl;
        cout << "╚══════════════════════════════════════════════════════╝" << endl;
        cout << "  User          : " << name << endl;
        cout << "  Questions     : " << totalQuestions << endl;
        cout << "  Correct       : " << correctAnswers << endl;
        cout << "  Wrong         : " << wrongAnswers << endl;
        cout << "  Hints Used    : " << hintsUsed << endl;
        cout << "  Avg Response  : " << (totalQuestions ? (totalResponseMs / totalQuestions) : 0) << " ms" << endl;
        cout << "  Weak Patterns  :" << endl;
        if (incorrectCategoryFrequency.empty())
            cout << "    - No repeated weak areas detected yet." << endl;
        else
        {
            int rank = 1;
            for (const auto &entry : incorrectCategoryFrequency)
            {
                cout << "    " << rank++ << ". " << entry.first
                     << " (" << entry.second << " incorrect attempts)" << endl;
            }
        }
        cout << "  Insight       : " << (wrongAnswers == 0 ? "Excellent precision. Keep the pace!" : "Focus on slower or repeated weak topics for next time.") << endl;
        cout << "  Payload Ready : Diagnostic profile compiled for demo review." << endl;
    }
};

class Student
{
public:
    string name;
    int score;
    vector<string> weakTopics;
    DiagnosticAgent diagnostics;

    Student(string n)
    {
        name = n;
        score = 0;
    }

    void addMark() { score++; }
    void resetScore() { score = 0; weakTopics.clear(); }

    void recordWeakTopic(const string &topic)
    {
        if (topic.empty())
            return;
        if (find(weakTopics.begin(), weakTopics.end(), topic) == weakTopics.end())
            weakTopics.push_back(topic);
    }

    void showRoadmap()
    {
        cout << "\n╔══════════════════════════════════════════════════════╗" << endl;
        cout << "║          PERSONALIZED ACADEMIC ROADMAP             ║" << endl;
        cout << "╚══════════════════════════════════════════════════════╝" << endl;
        if (weakTopics.empty())
        {
            cout << "║ Excellent work — your performance is strong.        ║" << endl;
            cout << "║ Continue reviewing mixed practice and stay curious. ║" << endl;
        }
        else
        {
            cout << "║ Focus areas to strengthen:                          ║" << endl;
            for (const string &topic : weakTopics)
            {
                cout << "║   • " << topic;
                for (size_t i = topic.length(); i < 45; ++i) cout << ' ';
                cout << "║" << endl;
            }
            cout << "║ Next step: revisit notes, solve extra practice, and ║" << endl;
            cout << "║ review the weak topics before your next quiz.      ║" << endl;
        }
        cout << "╚══════════════════════════════════════════════════════╝" << endl;
    }

    void showResult(int total)
    {
        float pct = ((float)score / total) * 100;
        cout << "\n╔══════════════════════════════════════════════════════╗" << endl;
        cout << "║                    QUIZ RESULT                      ║" << endl;
        cout << "╠══════════════════════════════════════════════════════╣" << endl;
        cout << "║ Name   : " << name;
        for (size_t i = name.length(); i < 42; ++i) cout << ' ';
        cout << "║" << endl;
        cout << "║ Score  : " << score << " / " << total;
        for (size_t i = to_string(score).length() + to_string(total).length() + 8; i < 42; ++i) cout << ' ';
        cout << "║" << endl;
        cout << "║ Marks  : " << fixed << setprecision(1) << pct << "%";
        for (size_t i = 0; i < 40; ++i) cout << ' ';
        cout << "║" << endl;
        cout << "║ Grade  : " << (pct >= 80 ? "A - Excellent!" : pct >= 60 ? "B - Good job!" : pct >= 40 ? "C - Need practice" : "F - Study more");
        for (size_t i = 0; i < 36; ++i) cout << ' ';
        cout << "║" << endl;
        cout << "╚══════════════════════════════════════════════════════╝" << endl;
        showRoadmap();
        diagnostics.printSummary(name);

        if (!weakTopics.empty())
        {
            cout << "\n  Generating study roadmap..." << endl;
            string aiRoadmap = generateAiRoadmap(name, weakTopics);
            cout << "\n  Study Roadmap\n  -------------\n";
            cout << aiRoadmap << endl;
        }

        cout << "\n  Press ENTER to return to menu...";
        cin.ignore();
        cin.get();
        clearScreen();
    }
};

class Quiz
{
public:
    string title;
    vector<Question*> questions;
    int count;
    bool stopped;

    Quiz(string t)
    {
        title = t;
        count = 0;
        stopped = false;
    }

    ~Quiz()
    {
        clearQuestions();
    }

    void addQuestion(Question *q)
    {
        questions.push_back(q);
        ++count;
    }

    void clearQuestions()
    {
        for (Question *q : questions)
        {
            delete q;
        }
        questions.clear();
        count = 0;
    }

    void loadQuestionsFromFile(const string &filename = "data/questions_db.txt", const string &subjectName = "")
    {
        clearQuestions();

        ifstream file(filename);
        if (!file.is_open())
        {
            cout << "\n  [Info] No question database found at '" << filename << "'." << endl;
            return;
        }

        string line;
        while (getline(file, line))
        {
            if (line.empty())
                continue;

            vector<string> parts;
            string part;
            stringstream ss(line);
            while (getline(ss, part, '|'))
                parts.push_back(part);

            if (parts.size() < 6)
                continue;

            string subject = parts[0];
            if (!subjectName.empty() && subject != subjectName)
                continue;

            Question *q = nullptr;
            if (parts.size() >= 9)
            {
                q = new Question(parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7], parts[8]);
            }
            else if (parts.size() == 8)
            {
                q = new Question(parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7]);
            }
            else if (parts.size() == 7)
            {
                q = new Question(parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]);
            }
            else
            {
                q = new Question(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]);
            }
            if (q) addQuestion(q);
        }
        file.close();

        if (count == 0)
            cout << "\n  [Info] No valid questions were loaded from '" << filename << "'." << endl;
        else
            cout << "\n  [Info] Loaded " << count << " question(s) from '" << filename << "' for '" << (subjectName.empty() ? "all subjects" : subjectName) << "'." << endl;
    }

    void shuffleQuestions()
    {
        if (count < 2)
            return;

        srand(static_cast<unsigned>(time(0)));
        for (int i = count - 1; i > 0; --i)
        {
            int j = rand() % (i + 1);
            swap(questions[i], questions[j]);
        }
    }

    int askWithTimer(Question *q, Student &student)
    {
        q->show();
        auto questionStart = chrono::steady_clock::now();
        cout << "\n  Controls: [A/B/C/D] Answer | HINT = AI clue | X = Stop Quiz" << endl;

        auto start = chrono::steady_clock::now();
        char userAns = ' ';
        bool usedHint = false;

        while (true)
        {
            auto now = chrono::steady_clock::now();
            auto elapsed = chrono::duration_cast<chrono::seconds>(now - start).count();
            int remaining = 30 - static_cast<int>(elapsed);

            if (remaining <= 0)
            {
                student.recordWeakTopic(q->hint.empty() ? q->text : q->hint);
                cout << "\n  [0s] TIME'S UP! No answer given." << endl;
                return 0;
            }

            cout << "\r  [Time: " << remaining << "s] Your Answer (A/B/C/D): _   ";
            cout.flush();

            if (cin.peek() != EOF)
            {
                char ch;
                string extra;
                cin >> ch;
                getline(cin, extra);
                string input = string(1, ch) + extra;
                string lower = toLowerCopy(input);

                if (lower == "hint")
                {
                    usedHint = true;
                    cout << "\n  Generating an offline hint...\n";
                    string aiHint = generateAiHint(q);
                    cout << "\n  Hint:\n" << aiHint << endl;
                    cout << "\n  Press ENTER to continue...";
                    cin.get();
                    clearScreen();
                    q->show();
                    cout << "\n  Controls: [A/B/C/D] Answer | HINT = AI clue | X = Stop Quiz" << endl;
                    cout << "\r  [Time: " << (30 - static_cast<int>(chrono::duration_cast<chrono::seconds>(chrono::steady_clock::now() - start).count())) << "s] Your Answer (A/B/C/D): _   ";
                    cout.flush();
                    continue;
                }

                ch = static_cast<char>(toupper(static_cast<unsigned char>(ch)));
                if (ch >= 'A' && ch <= 'D')
                {
                    userAns = ch;
                    break;
                }
                if (ch == 'X')
                {
                    cout << "\n\n  Quiz has been stopped!\n";
                    return -1;
                }
            }

            this_thread::sleep_for(chrono::milliseconds(200));
        }

        auto responseMs = chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now() - questionStart).count();
        cout << "\r  Your Answer: " << userAns << "                              " << endl;

        string ans(1, userAns);
        bool isCorrect = (ans == q->answer);
        student.diagnostics.recordAnswer(responseMs, isCorrect, q->hint.empty() ? q->text : q->hint, usedHint);
        if (ans == q->answer)
        {
            cout << "  >> CORRECT! Well done!" << endl;
            return 2;
        }
        else
        {
            student.recordWeakTopic(q->hint.empty() ? q->text : q->hint);
            cout << "  >> WRONG! Correct answer was: " << q->answer << endl;
            return 1;
        }
    }

    void start(Student &student)
    {
        stopped = false;
        student.resetScore();
        shuffleQuestions();

        cout << "\n╔══════════════════════════════════════════════════════╗" << endl;
        cout << "║                QUIZ START PANEL                    ║" << endl;
        cout << "╠══════════════════════════════════════════════════════╣" << endl;
        cout << "| Subject   : " << title;
        for (size_t i = title.length(); i < 43; ++i) cout << ' ';
        cout << "|" << endl;
        cout << "| Questions : " << count;
        for (size_t i = to_string(count).length(); i < 40; ++i) cout << ' ';
        cout << "|" << endl;
        cout << "║ Time/Q    : 30 seconds                            ║" << endl;
        cout << "╚══════════════════════════════════════════════════════╝" << endl;
        cout << "\n  Press ENTER to start (Type X + ENTER to Cancel): ";

        string inp;
        getline(cin, inp);
        if (inp == "X" || inp == "x")
        {
            cout << "  Quiz cancelled." << endl;
            cout << "\n  Press ENTER to return to menu...";
            cin.get();
            clearScreen();
            return;
        }

        cout << "\n  Quiz is starting now...\n" << endl;

        for (int i = 0; i < count; ++i)
        {
            cout << "\n╔══════════════════════════════════════════════════════╗" << endl;
            cout << "║ Question " << (i + 1) << " / " << count;
            for (size_t j = to_string(i + 1).length() + to_string(count).length() + 11; j < 47; ++j) cout << ' ';
            cout << "║" << endl;
            cout << "╚══════════════════════════════════════════════════════╝" << endl;

            int result = askWithTimer(questions[i], student);

            if (result == -1)
            {
                stopped = true;
                cout << "\n  Score so far: " << student.score << "/" << i << endl;
                cout << "\n  Press ENTER to return to menu...";
                cin.ignore();
                cin.get();
                clearScreen();
                return;
            }
            if (result == 2)
                student.addMark();
        }

        student.showResult(count);
    }
};

class PerformanceHistory
{
public:
    void appendResult(const string &username, const string &quiz, int score, int total, const vector<string> &weakTopics)
    {
        ofstream file("history.txt", ios::app);
        if (!file.is_open())
            return;

        time_t now = time(nullptr);
        char dateBuf[64];
        strftime(dateBuf, sizeof(dateBuf), "%Y-%m-%d %H:%M", localtime(&now));

        file << username << "|" << quiz << "|" << score << "|" << total << "|"
             << fixed << setprecision(1) << (100.0f * score / total) << "|" << dateBuf << "|";
        for (size_t i = 0; i < weakTopics.size(); ++i)
        {
            if (i) file << ",";
            file << weakTopics[i];
        }
        file << "\n";
        file.close();
    }

    void showRecentChart(const string &username)
    {
        ifstream file("history.txt");
        if (!file.is_open())
        {
            cout << "\n  No history found yet.\n";
            return;
        }

        vector<pair<int, string>> scores;
        string line;
        while (getline(file, line))
        {
            if (line.empty()) continue;
            size_t p1 = line.find('|');
            size_t p2 = line.find('|', p1 + 1);
            size_t p3 = line.find('|', p2 + 1);
            size_t p4 = line.find('|', p3 + 1);
            size_t p5 = line.find('|', p4 + 1);
            if (p1 == string::npos || p5 == string::npos) continue;
            if (line.substr(0, p1) != username) continue;
            int score = stoi(line.substr(p2 + 1, p3 - p2 - 1));
            int total = stoi(line.substr(p3 + 1, p4 - p3 - 1));
            int pct = static_cast<int>((100.0f * score) / total);
            scores.push_back({pct, line.substr(p1 + 1, p2 - p1 - 1)});
        }

        if (scores.empty())
        {
            cout << "\n  No quiz history for you yet.\n";
            return;
        }

        reverse(scores.begin(), scores.end());
        if (scores.size() > 5) scores.resize(5);

        cout << "\n  ===== YOUR LAST 5 QUIZ SCORES =====\n";
        int maxPct = 0;
        for (const auto &entry : scores) if (entry.first > maxPct) maxPct = entry.first;
        for (const auto &entry : scores)
        {
            int bars = (entry.first * 30) / (maxPct > 0 ? maxPct : 100);
            cout << "  " << entry.second << " | ";
            for (int i = 0; i < bars; ++i) cout << "█";
            for (int i = bars; i < 30; ++i) cout << "-";
            cout << " " << entry.first << "%\n";
        }
    }
};

class FileHandler
{
public:
    void saveUser(string username, string password)
    {
        ofstream file("users.txt", ios::app);
        if (file.is_open())
        {
            file << username << "|" << password << "\n";
            file.close();
            cout << "\n  [OK] User saved successfully!" << endl;
        }
        else
        {
            cout << "\n  [Error] Could not save user!" << endl;
        }
    }

    bool loginUser(string username, string password)
    {
        ifstream file("users.txt");
        if (!file.is_open())
            return false;
        string line;
        while (getline(file, line))
        {
            size_t pos = line.find("|");
            if (pos != string::npos)
            {
                if (line.substr(0, pos) == username &&
                    line.substr(pos + 1) == password)
                {
                    file.close();
                    return true;
                }
            }
        }
        file.close();
        return false;
    }

    bool userExists(string username)
    {
        ifstream file("users.txt");
        if (!file.is_open())
            return false;
        string line;
        while (getline(file, line))
        {
            size_t pos = line.find("|");
            if (pos != string::npos && line.substr(0, pos) == username)
            {
                file.close();
                return true;
            }
        }
        file.close();
        return false;
    }

    void saveResult(string user, string quiz, int score, int total)
    {
        float pct = ((float)score / total) * 100;
        string grade = "F";
        if (pct >= 80)
            grade = "A";
        else if (pct >= 60)
            grade = "B";
        else if (pct >= 40)
            grade = "C";

        ofstream file("results.txt", ios::app);
        if (file.is_open())
        {
            file << user << "|" << quiz << "|" << score << "|"
                 << total << "|" << pct << "|" << grade << "\n";
            file.close();
            cout << "  [OK] Result saved!" << endl;
        }
    }

    void showMyResults(string username)
    {
        ifstream file("results.txt");
        if (!file.is_open())
        {
            cout << "\n  No results file found!\n";
            return;
        }

        cout << "\n ================================" << endl;
        cout << "  YOUR RESULTS: " << username << endl;
        cout << " ================================" << endl;

        string line;
        bool found = false;
        while (getline(file, line))
        {
            if (line.empty())
                continue;
            size_t p1 = line.find("|");
            size_t p2 = line.find("|", p1 + 1);
            size_t p3 = line.find("|", p2 + 1);
            size_t p4 = line.find("|", p3 + 1);
            size_t p5 = line.find("|", p4 + 1);
            if (p1 == string::npos || p5 == string::npos)
                continue;
            if (line.substr(0, p1) == username)
            {
                cout << "\n  Quiz    : " << line.substr(p1 + 1, p2 - p1 - 1) << endl;
                cout << "  Score   : " << line.substr(p2 + 1, p3 - p2 - 1)
                     << " / " << line.substr(p3 + 1, p4 - p3 - 1) << endl;
                cout << "  Percent : " << line.substr(p4 + 1, p5 - p4 - 1) << "%" << endl;
                cout << "  Grade   : " << line.substr(p5 + 1) << endl;
                found = true;
            }
        }
        if (!found)
            cout << "  No results found for you yet!\n";
        file.close();
    }

    void showAllResults()
    {
        ifstream file("results.txt");
        if (!file.is_open())
        {
            cout << "\n  No results file found!\n";
            return;
        }

        cout << "\n ================================" << endl;
        cout << "     ALL STUDENTS RESULTS" << endl;
        cout << " ================================" << endl;

        string line;
        bool found = false;
        while (getline(file, line))
        {
            if (line.empty())
                continue;
            size_t p1 = line.find("|");
            size_t p2 = line.find("|", p1 + 1);
            size_t p3 = line.find("|", p2 + 1);
            size_t p4 = line.find("|", p3 + 1);
            size_t p5 = line.find("|", p4 + 1);
            if (p1 == string::npos || p5 == string::npos)
                continue;
            cout << "\n  User: " << line.substr(0, p1)
                 << " | Quiz: " << line.substr(p1 + 1, p2 - p1 - 1)
                 << " | Score: " << line.substr(p2 + 1, p3 - p2 - 1)
                 << "/" << line.substr(p3 + 1, p4 - p3 - 1)
                 << " | " << line.substr(p4 + 1, p5 - p4 - 1)
                 << "% | Grade: " << line.substr(p5 + 1) << endl;
            found = true;
        }
        if (!found)
            cout << "  No results found!\n";
        file.close();
    }

    void showAllUsers()
    {
        ifstream file("users.txt");
        if (!file.is_open())
        {
            cout << "\n  No users file found!\n";
            return;
        }

        cout << "\n ================================" << endl;
        cout << "     REGISTERED USERS" << endl;
        cout << " ================================" << endl;

        string line;
        bool found = false;
        while (getline(file, line))
        {
            size_t pos = line.find("|");
            if (pos != string::npos)
            {
                cout << "  - " << line.substr(0, pos) << endl;
                found = true;
            }
        }
        if (!found)
            cout << "  No users found!\n";
        file.close();
    }
};

int main()
{

    FileHandler fh;
    PerformanceHistory history;

    Quiz pythonQuiz("Python Programming");
    pythonQuiz.loadQuestionsFromFile("data/questions_db.txt", "Python Programming");

    Quiz mathQuiz("Mathematics");
    mathQuiz.loadQuestionsFromFile("data/questions_db.txt", "Mathematics");

    Quiz progQuiz("Programming Basics");
    progQuiz.loadQuestionsFromFile("data/questions_db.txt", "Programming Basics");

    Quiz calcQuiz("Calculus");
    calcQuiz.loadQuestionsFromFile("data/questions_db.txt", "Calculus");

    Quiz engQuiz("English");
    engQuiz.loadQuestionsFromFile("data/questions_db.txt", "English");

    clearScreen();
    cout << "\n ========================================" << endl;
    cout << "        ONLINE QUIZ SYSTEM              " << endl;
    cout << " ========================================" << endl;
    cout << "          Welcome to the Portal!        " << endl;
    cout << " ========================================" << endl;

    const string ADMIN_USER = "admin";
    const string ADMIN_PASS = "admin123";

    int mainChoice;
    do
    {
        while (true)
        {
            cout << "\n ======= MAIN MENU =======" << endl;
            cout << " 1. Student Login" << endl;
            cout << " 2. Admin Login" << endl;
            cout << " 3. Sign Up" << endl;
            cout << " 4. Exit" << endl;
            cout << " Enter choice: ";
            if (!(cin >> mainChoice))
            {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cout << "  Invalid input. Please enter a number.\n";
                continue;
            }
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            if (mainChoice >= 1 && mainChoice <= 4) break;
            cout << "  Invalid choice! Please enter 1 to 4.\n";
        }

        if (mainChoice == 1)
        {
            string username, password;
            cout << "\n ======= STUDENT LOGIN =======" << endl;
            cout << "  Username: ";
            getline(cin, username);
            password = getMaskedPassword();

            if (fh.loginUser(username, password))
            {
                clearScreen();

                cout << "\n ========================================" << endl;
                cout << "        ONLINE QUIZ SYSTEM              " << endl;
                cout << " ========================================" << endl;
                cout << "   Welcome, " << username << "!" << endl;
                cout << " ========================================" << endl;
                cout << "\n  Press ENTER to continue...";
                cin.get();
                clearScreen();

                Student student(username);
                int choice;
                do
                {
                    cout << "\n ========================================" << endl;
                    cout << "        ONLINE QUIZ SYSTEM              " << endl;
                    cout << " ========================================" << endl;
                    while (true)
                    {
                        cout << "\n ======= STUDENT MENU =======" << endl;
                        cout << " 1. Python Programming  (" << pythonQuiz.count << " Q)" << endl;
                        cout << " 2. Mathematics         (" << mathQuiz.count << " Q)" << endl;
                        cout << " 3. Programming Basics  (" << progQuiz.count << " Q)" << endl;
                        cout << " 4. Calculus            (" << calcQuiz.count << " Q)" << endl;
                        cout << " 5. English             (" << engQuiz.count << " Q)" << endl;
                        cout << " 6. My Results" << endl;
                        cout << " 7. History Chart" << endl;
                        cout << " 8. Logout" << endl;
                        cout << " Enter choice: ";
                        if (!(cin >> choice))
                        {
                            cin.clear();
                            cin.ignore(numeric_limits<streamsize>::max(), '\n');
                            cout << "  Invalid input. Please enter a number.\n";
                            continue;
                        }
                        cin.ignore(numeric_limits<streamsize>::max(), '\n');
                        if (choice >= 1 && choice <= 8) break;
                        cout << "  Invalid choice! Please enter 1 to 8.\n";
                    }

                    if (choice == 1)
                    {
                        pythonQuiz.start(student);
                        if (!pythonQuiz.stopped)
                        {
                            fh.saveResult(username, "Python Programming", student.score, pythonQuiz.count);
                            history.appendResult(username, "Python Programming", student.score, pythonQuiz.count, student.weakTopics);
                        }
                    }
                    else if (choice == 2)
                    {
                        mathQuiz.start(student);
                        if (!mathQuiz.stopped)
                        {
                            fh.saveResult(username, "Mathematics", student.score, mathQuiz.count);
                            history.appendResult(username, "Mathematics", student.score, mathQuiz.count, student.weakTopics);
                        }
                    }
                    else if (choice == 3)
                    {
                        progQuiz.start(student);
                        if (!progQuiz.stopped)
                        {
                            fh.saveResult(username, "Programming Basics", student.score, progQuiz.count);
                            history.appendResult(username, "Programming Basics", student.score, progQuiz.count, student.weakTopics);
                        }
                    }
                    else if (choice == 4)
                    {
                        calcQuiz.start(student);
                        if (!calcQuiz.stopped)
                        {
                            fh.saveResult(username, "Calculus", student.score, calcQuiz.count);
                            history.appendResult(username, "Calculus", student.score, calcQuiz.count, student.weakTopics);
                        }
                    }
                    else if (choice == 5)
                    {
                        engQuiz.start(student);
                        if (!engQuiz.stopped)
                        {
                            fh.saveResult(username, "English", student.score, engQuiz.count);
                            history.appendResult(username, "English", student.score, engQuiz.count, student.weakTopics);
                        }
                    }
                    else if (choice == 6)
                    {
                        fh.showMyResults(username);
                    }
                    else if (choice == 7)
                    {
                        history.showRecentChart(username);
                    }
                    else if (choice == 8)
                    {
                        clearScreen();
                        cout << "\n  You have been logged out!\n";
                    }
                    else
                    {
                        cout << "  Invalid choice!\n";
                    }

                } while (choice != 8);
            }
            else
            {
                cout << "\n  Invalid username or password!\n";
            }
        }
        else if (mainChoice == 2)
        {
            string username, password;
            cout << "\n ======= ADMIN LOGIN =======" << endl;
            cout << "  Username: ";
            getline(cin, username);
            password = getMaskedPassword();

            if (username == ADMIN_USER && password == ADMIN_PASS)
            {
                clearScreen();
                int adminChoice;
                do
                {
                    cout << "\n ========================================" << endl;
                    cout << "        ONLINE QUIZ SYSTEM              " << endl;
                    cout << " ========================================" << endl;
                    cout << "          Welcome, Admin!               " << endl;
                    cout << " ========================================" << endl;
                    while (true)
                    {
                        cout << "\n ======= ADMIN MENU =======" << endl;
                        cout << " 1. View All Users" << endl;
                        cout << " 2. View All Results" << endl;
                        cout << " 3. Logout" << endl;
                        cout << " Enter choice: ";
                        if (!(cin >> adminChoice))
                        {
                            cin.clear();
                            cin.ignore(numeric_limits<streamsize>::max(), '\n');
                            cout << "  Invalid input. Please enter a number.\n";
                            continue;
                        }
                        cin.ignore(numeric_limits<streamsize>::max(), '\n');
                        if (adminChoice >= 1 && adminChoice <= 3) break;
                        cout << "  Invalid choice! Please enter 1 to 3.\n";
                    }

                    if (adminChoice == 1)
                    {
                        fh.showAllUsers();
                    }
                    else if (adminChoice == 2)
                    {
                        fh.showAllResults();
                    }
                    else if (adminChoice == 3)
                    {
                        clearScreen();
                        cout << "\n  Admin logged out!\n";
                    }
                    else
                    {
                        cout << "  Invalid choice!\n";
                    }

                } while (adminChoice != 3);
            }
            else
            {
                cout << "\n  Invalid admin credentials!\n";
            }
        }
        else if (mainChoice == 3)
        {
            string newUser, pass1, pass2;
            cout << "\n ======= SIGN UP =======" << endl;
            cout << "  Username: ";
            getline(cin, newUser);

            if (newUser == ADMIN_USER)
            {
                cout << "  This username is reserved. Choose another.\n";
            }
            else if (fh.userExists(newUser))
            {
                cout << "  Username already exists!\n";
            }
            else
            {
                pass1 = getMaskedPassword();
                pass2 = getMaskedPassword("  Confirm : ");

                if (pass1 != pass2)
                {
                    cout << "  Passwords do not match!\n";
                }
                else if (!isStrongPassword(pass1))
                {
                    cout << "  Password must be at least 8 characters and include letters, numbers, and one special symbol!\n";
                }
                else
                {
                    fh.saveUser(newUser, pass1);
                    cout << "\n  Account created successfully!" << endl;
                    cout << "  Please login with your new account." << endl;
                    this_thread::sleep_for(chrono::milliseconds(1500));
                    clearScreen();
                }
            }
        }
        else if (mainChoice == 4)
        {
            clearScreen();
            cout << "\n ========================================" << endl;
            cout << "        ONLINE QUIZ SYSTEM              " << endl;
            cout << " ========================================" << endl;
            cout << "  Thank you for using the Quiz System!  " << endl;
            cout << "              Goodbye!                  " << endl;
            cout << " ========================================" << endl;
        }
        else
        {
            cout << "  Invalid choice!\n";
        }

    } while (mainChoice != 4);

    return 0;
}