import os
import sys
import requests
import json
import re

TOKEN = os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    print("Error: GITHUB_TOKEN environment variable is missing.")
    sys.exit(1)

USER = "pranay213"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

os.makedirs("assets", exist_ok=True)

def fetch_data():
    query_repos = """
    query {
      user(login: "%s") {
        repositories(first: 100, isFork: false, privacy: PUBLIC) {
          totalCount
          nodes {
            name
            description
            stargazerCount
            primaryLanguage {
              name
              color
            }
          }
        }
        followers {
          totalCount
        }
        following {
          totalCount
        }
      }
    }
    """ % USER

    print("Fetching repositories data...")
    res_repos = requests.post("https://api.github.com/graphql", json={"query": query_repos}, headers=HEADERS)
    if res_repos.status_code != 200:
        print(f"Error fetching repos: {res_repos.status_code}")
        sys.exit(1)

    json_repos = res_repos.json()
    if "errors" in json_repos:
        print("GraphQL Errors detected!")
        print("Repos error:", json.dumps(json_repos["errors"], indent=2))
        sys.exit(1)

    print("Fetching activity calendar data via HTML scraping to bypass API limits...")
    html = requests.get(f"https://github.com/users/{USER}/contributions").text
    levels = re.findall(r'data-level="(\d+)"', html)
    activity = [int(l) for l in levels[-35*7:]] if levels else [0]*(35*7)
    
    total_match = re.search(r'([\d,]+)\s+contributions', html)
    total_contribs = int(total_match.group(1).replace(',', '')) if total_match else 0

    print("Fetching radar stats via REST Search API to bypass limits...")
    def get_search_count(q, endpoint="issues"):
        res = requests.get(f"https://api.github.com/search/{endpoint}?q={q}", headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("total_count", 0)
        return 0

    issues_count = get_search_count(f"author:{USER} type:issue")
    prs_count = get_search_count(f"author:{USER} type:pr")
    reviews_count = get_search_count(f"reviewed-by:{USER} type:pr")
    commits_count = get_search_count(f"author:{USER}", endpoint="commits")

    data_repos = json_repos["data"]["user"]
    
    repos = data_repos["repositories"]["nodes"]
    total_repos = data_repos["repositories"]["totalCount"]
    total_stars = sum(r["stargazerCount"] for r in repos)
    
    lang_counts = {}
    for r in repos:
        if r["primaryLanguage"]:
            lang = r["primaryLanguage"]["name"]
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            
    total_lang = sum(lang_counts.values()) or 1
    langs = {k: round((v/total_lang)*100, 1) for k, v in sorted(lang_counts.items(), key=lambda item: item[1], reverse=True)[:5]}
    
    top_repos = sorted(repos, key=lambda x: x["stargazerCount"], reverse=True)[:4]

    return {
        "repos": total_repos,
        "stars": total_stars,
        "followers": data_repos["followers"]["totalCount"],
        "following": data_repos["following"]["totalCount"],
        "contributions": total_contribs,
        "pinned": top_repos,
        "langs": langs,
        "activity": activity,
        "radar": {
            "commits": commits_count,
            "issues": issues_count,
            "prs": prs_count,
            "reviews": reviews_count
        }
    }


def generate_svgs(data):
    print("Generating SVGs with real-time data...")
    BG = "#0d1117"
    BORDER = "#30363d"
    TEXT = "#c9d1d9"
    HEADING = "#ffffff"
    GREEN = "#3fb950"
    BLUE = "#58a6ff"
    font_family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono_family = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace"

    intro_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 350" width="100%" height="100%">
        <style>
            @keyframes typing {{ from {{ width: 0; }} to {{ width: 100%; }} }}
            @keyframes blink {{ 50% {{ opacity: 0; }} }}
            @keyframes slideIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes float {{ 0% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); }} 100% {{ transform: translateY(0px); }} }}
            .text-slide {{ animation: slideIn 0.8s ease-out forwards; opacity: 0; }}
            .t1 {{ animation-delay: 0.1s; }} .t2 {{ animation-delay: 0.2s; }} .t3 {{ animation-delay: 0.3s; }}
            .t4 {{ animation-delay: 0.4s; }} .t5 {{ animation-delay: 0.5s; }} .t6 {{ animation-delay: 0.6s; }}
            .t7 {{ animation-delay: 0.7s; }} .t8 {{ animation-delay: 0.8s; }}
            .terminal-window {{ animation: float 6s ease-in-out infinite; }}
        </style>
        <rect width="1000" height="340" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
        <text x="30" y="50" font-family="{font_family}" font-size="28" font-weight="600" fill="{HEADING}" class="text-slide t1">Hi there! 👋 I'm Pranay Kumar Kodam</text>
        <g font-family="{font_family}" font-size="14" fill="{TEXT}">
            <text x="30" y="90" class="text-slide t2">💻 Full Stack Developer with 6+ years of experience</text>
            <text x="30" y="125" class="text-slide t3">⚡ Expertise in React, Next.js, Node.js, React Native, MongoDB</text>
            <text x="30" y="160" class="text-slide t4">☁️ Experienced with AWS, GCP, Docker &amp; CI/CD</text>
            <text x="30" y="195" class="text-slide t5">🎯 Passionate about building real-world products</text>
            <text x="30" y="230" class="text-slide t6">🔭 Currently exploring <tspan fill="{BLUE}">Go</tspan>, System Design &amp; DevOps</text>
            <text x="30" y="265" class="text-slide t7">💬 Ask me about JavaScript, TypeScript, React, Node.js</text>
            <text x="30" y="300" class="text-slide t8">📫 Reach me: <tspan fill="{BLUE}" text-decoration="underline">pranaykodam.213@gmail.com</tspan></text>
        </g>
        <g transform="translate(530, 25)" class="terminal-window">
            <rect width="440" height="290" rx="6" fill="#010409" stroke="{BORDER}" stroke-width="1"/>
            <circle cx="20" cy="20" r="5" fill="#ff5f56"/>
            <circle cx="40" cy="20" r="5" fill="#ffbd2e"/>
            <circle cx="60" cy="20" r="5" fill="#27c93f"/>
            <g font-family="{mono_family}" font-size="13">
                <text x="15" y="60" fill="{GREEN}">pranay@github<tspan fill="{TEXT}">:~$ whoami</tspan></text>
                <text x="15" y="85" fill="{TEXT}">Full Stack Developer</text>
                <text x="15" y="115" fill="{GREEN}">pranay@github<tspan fill="{TEXT}">:~$ skills --list</tspan></text>
                <text x="15" y="140" fill="{TEXT}">JavaScript, TypeScript, React, Next.js,</text>
                <text x="15" y="165" fill="{TEXT}">Node.js, Express.js, MongoDB, PostgreSQL,</text>
                <text x="15" y="190" fill="{TEXT}">React Native, Expo, AWS, Docker, Go,</text>
                <text x="15" y="215" fill="{TEXT}">Redis, RabbitMQ, CI/CD, Git, Linux</text>
                <text x="15" y="245" fill="{GREEN}">pranay@github<tspan fill="{TEXT}">:~$ status</tspan></text>
                <text x="15" y="270" fill="{TEXT}">Building the future 🌍</text>
            </g>
        </g>
    </svg>"""

    stats_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" width="100%" height="100%">
        <style>
            @keyframes scaleIn {{ from {{ opacity: 0; transform: scale(0.9) translateY(10px); }} to {{ opacity: 1; transform: scale(1) translateY(0); }} }}
            .stat-card {{ animation: scaleIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; opacity: 0; }}
            .s1 {{ animation-delay: 0.1s; }} .s2 {{ animation-delay: 0.2s; }} .s3 {{ animation-delay: 0.3s; }}
            .s4 {{ animation-delay: 0.4s; }} .s5 {{ animation-delay: 0.5s; }}
        </style>
        <g transform="translate(0, 10)">
            <g class="stat-card s1" transform-origin="95px 40px">
                <rect x="0" y="0" width="190" height="80" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
                <text x="70" y="35" font-family="{font_family}" font-size="14" fill="{BLUE}" font-weight="600">Repositories</text>
                <text x="70" y="65" font-family="{font_family}" font-size="24" fill="{HEADING}" font-weight="600">{data["repos"]}</text>
            </g>
            
            <g class="stat-card s2" transform-origin="297px 40px">
                <rect x="202" y="0" width="190" height="80" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
                <text x="272" y="35" font-family="{font_family}" font-size="14" fill="#e3b341" font-weight="600">Stars Earned</text>
                <text x="272" y="65" font-family="{font_family}" font-size="24" fill="{HEADING}" font-weight="600">{data["stars"]}</text>
            </g>
            
            <g class="stat-card s3" transform-origin="500px 40px">
                <rect x="405" y="0" width="190" height="80" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
                <text x="475" y="35" font-family="{font_family}" font-size="14" fill="#a371f7" font-weight="600">Contributions</text>
                <text x="475" y="65" font-family="{font_family}" font-size="24" fill="{HEADING}" font-weight="600">{data["contributions"]}</text>
            </g>
            
            <g class="stat-card s4" transform-origin="702px 40px">
                <rect x="607" y="0" width="190" height="80" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
                <text x="677" y="35" font-family="{font_family}" font-size="14" fill="#a371f7" font-weight="600">Followers</text>
                <text x="677" y="65" font-family="{font_family}" font-size="24" fill="{HEADING}" font-weight="600">{data["followers"]}</text>
            </g>
            
            <g class="stat-card s5" transform-origin="905px 40px">
                <rect x="810" y="0" width="190" height="80" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
                <text x="880" y="35" font-family="{font_family}" font-size="14" fill="#3fb950" font-weight="600">Following</text>
                <text x="880" y="65" font-family="{font_family}" font-size="24" fill="{HEADING}" font-weight="600">{data["following"]}</text>
            </g>
        </g>
    </svg>"""

    activity = data["activity"]
    activity_grid = ""
    for i, count in enumerate(activity):
        c = i // 7
        r = i % 7
        colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
        color = colors[count] if count < len(colors) else "#39d353"
        delay = (c + r) * 0.02
        activity_grid += f'<rect x="{c*15}" y="{r*15}" width="11" height="11" rx="2" fill="{color}" class="grid-cell" style="animation-delay: {delay}s" />'

    lang_legend = ""
    colors = ["#3178c6", "#f1e05a", "#e34c26", "#563d7c", "#8b949e"]
    if data["langs"]:
        for i, (lang, pct) in enumerate(data["langs"].items()):
            c = colors[i % len(colors)]
            delay = i * 0.15
            lang_legend += f'<g class="lang-item" style="animation-delay: {delay}s"><circle cx="0" cy="{i*30 - 5}" r="5" fill="{c}"/> <text x="15" y="{i*30}" fill="{TEXT}">{lang}</text> <text x="100" y="{i*30}" fill="{TEXT}">{pct}%</text></g>'
    else:
        lang_legend = f'<text x="15" y="0" fill="{TEXT}">No public code detected</text>'

    charts_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" width="100%" height="100%">
        <style>
            @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes drawCircle {{ from {{ stroke-dasharray: 0 400; }} to {{ stroke-dasharray: 150 400; }} }}
            .grid-cell {{ animation: fadeUp 0.3s ease forwards; opacity: 0; }}
            .lang-item {{ animation: fadeUp 0.5s ease forwards; opacity: 0; }}
            .chart-ring {{ animation: drawCircle 1.5s ease-out forwards; }}
        </style>
        <rect x="0" y="10" width="590" height="280" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
        <text x="25" y="45" font-family="{font_family}" font-size="16" fill="{HEADING}" font-weight="600">📈 GitHub Activity</text>
        <text x="25" y="75" font-family="{font_family}" font-size="14" fill="{TEXT}">{data["contributions"]:,} contributions in the last year</text>
        <g transform="translate(25, 100)">
            {activity_grid}
        </g>
        <rect x="610" y="10" width="390" height="280" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
        <text x="635" y="45" font-family="{font_family}" font-size="16" fill="{HEADING}" font-weight="600">🏆 Top Languages</text>
        <g transform="translate(700, 160)">
            <circle cx="0" cy="0" r="60" fill="none" stroke="#3178c6" stroke-width="30" class="chart-ring" transform="rotate(-90)" />
            <circle cx="0" cy="0" r="45" fill="{BG}" />
        </g>
        <g font-family="{font_family}" font-size="13" transform="translate(800, 100)">
            {lang_legend}
        </g>
    </svg>"""

    repos = data["pinned"]
    repo_svgs = ""
    coords = [(0,0), (285,0), (0, 120), (285, 120)]
    for i, r in enumerate(repos):
        if i >= len(coords): break
        x, y = coords[i]
        name = r["name"]
        desc = (r["description"] or "")[:40] + ("..." if len(r["description"] or "") > 40 else "")
        stars = r["stargazerCount"]
        lang = r["primaryLanguage"]["name"] if r["primaryLanguage"] else "Markdown"
        delay = i * 0.15
        repo_svgs += f"""
        <g class="repo-card" style="animation-delay: {delay}s">
            <rect x="{x}" y="{y}" width="265" height="105" rx="6" fill="#010409" stroke="{BORDER}" stroke-width="1"/>
            <text x="{x+15}" y="{y+25}" font-family="{font_family}" font-size="14" fill="{BLUE}" font-weight="600">{name}</text>
            <text x="{x+15}" y="{y+50}" font-family="{font_family}" font-size="12" fill="{TEXT}">{desc}</text>
            <circle cx="{x+20}" cy="{y+85}" r="5" fill="#3178c6"/> <text x="{x+35}" y="{y+89}" font-family="{font_family}" font-size="12" fill="{TEXT}">{lang}</text>
            <text x="{x+120}" y="{y+89}" font-family="{font_family}" font-size="12" fill="{TEXT}">⭐ {stars}</text>
        </g>
        """

    repos_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 320" width="100%" height="100%">
        <style>
            @keyframes slideRight {{ from {{ opacity: 0; transform: translateX(-20px); }} to {{ opacity: 1; transform: translateX(0); }} }}
            @keyframes drawPolygon {{ from {{ stroke-dashoffset: 1000; }} to {{ stroke-dashoffset: 0; }} }}
            @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            .repo-card {{ animation: slideRight 0.6s ease forwards; opacity: 0; }}
            .radar-polygon {{ stroke-dasharray: 1000; stroke-dashoffset: 1000; animation: drawPolygon 2s ease forwards; animation-delay: 0.5s; }}
            .radar-fill {{ animation: fadeUp 1s ease forwards; opacity: 0; animation-delay: 1.5s; }}
        </style>
        <rect x="0" y="10" width="590" height="300" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
        <text x="25" y="45" font-family="{font_family}" font-size="16" fill="{HEADING}" font-weight="600">📌 Top Public Repositories</text>
        <g transform="translate(20, 70)">
            {repo_svgs}
        </g>
        <rect x="610" y="10" width="390" height="300" rx="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
        <text x="635" y="45" font-family="{font_family}" font-size="16" fill="{HEADING}" font-weight="600">📊 Contribution Stats</text>
        <g transform="translate(805, 175)">
            <polygon points="0,-80 76,-24 47,64 -47,64 -76,-24" fill="none" stroke="{BORDER}" stroke-width="1" class="radar-polygon"/>
            <polygon points="0,-60 57,-18 35,48 -35,48 -57,-18" fill="none" stroke="{BORDER}" stroke-width="1" class="radar-polygon" style="animation-delay: 0.6s"/>
            <polygon points="0,-40 38,-12 23,32 -23,32 -38,-12" fill="none" stroke="{BORDER}" stroke-width="1" class="radar-polygon" style="animation-delay: 0.7s"/>
            <line x1="0" y1="0" x2="0" y2="-80" stroke="{BORDER}" stroke-width="1" class="radar-polygon" style="animation-delay: 0.8s"/>
            <line x1="0" y1="0" x2="76" y2="-24" stroke="{BORDER}" stroke-width="1" class="radar-polygon" style="animation-delay: 0.9s"/>
            <line x1="0" y1="0" x2="47" y2="64" stroke="{BORDER}" stroke-width="1" class="radar-polygon" style="animation-delay: 1.0s"/>
            <line x1="0" y1="0" x2="-47" y2="64" stroke="{BORDER}" stroke-width="1" class="radar-polygon" style="animation-delay: 1.1s"/>
            <line x1="0" y1="0" x2="-76" y2="-24" stroke="{BORDER}" stroke-width="1" class="radar-polygon" style="animation-delay: 1.2s"/>
            <polygon points="0,-70 60,-19 40,50 -20,30 -65,-20" fill="rgba(63, 185, 80, 0.2)" stroke="#3fb950" stroke-width="2" class="radar-fill"/>
            <text x="0" y="-95" font-family="{font_family}" font-size="12" fill="{TEXT}" text-anchor="middle">Code</text>
            <text x="100" y="-20" font-family="{font_family}" font-size="12" fill="{TEXT}" text-anchor="middle">Issues</text>
            <text x="70" y="85" font-family="{font_family}" font-size="12" fill="{TEXT}" text-anchor="middle">Pull Requests</text>
            <text x="-70" y="85" font-family="{font_family}" font-size="12" fill="{TEXT}" text-anchor="middle">Projects</text>
            <text x="-100" y="-20" font-family="{font_family}" font-size="12" fill="{TEXT}" text-anchor="middle">Reviews</text>
        </g>
    </svg>"""

    with open('assets/intro.svg', 'w') as f: f.write(intro_svg)
    with open('assets/stats.svg', 'w') as f: f.write(stats_svg)
    with open('assets/charts.svg', 'w') as f: f.write(charts_svg)
    with open('assets/repos.svg', 'w') as f: f.write(repos_svg)
    print("Successfully generated all SVGs.")

if __name__ == "__main__":
    data = fetch_data()
    generate_svgs(data)
