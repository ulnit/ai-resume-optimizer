#!/usr/bin/env python3
"""
AI Resume Optimizer — Analyze, enhance, and format resumes.
ATS-friendly. Keyword-optimized. Industry-specific.
"""
import re, json, sys
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(__file__).parent.parent

# Industry keyword banks
INDUSTRIES = {
    "tech": {
        "keywords": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes", "CI/CD", "Agile", "API", "microservices", "cloud", "ML", "AI", "React", "Node.js", "SQL", "NoSQL"],
        "verbs": ["Architected", "Engineered", "Optimized", "Deployed", "Automated", "Scaled", "Migrated", "Orchestrated"],
        "metrics": ["reduced latency by X%", "scaled to X users", "saved $X annually", "improved performance X%", "handled X requests/sec"]
    },
    "finance": {
        "keywords": ["Financial Modeling", "Risk Analysis", "Bloomberg", "Excel", "VBA", "CFA", "FRM", "P&L", "Valuation", "Derivatives", "Portfolio", "Quant"],
        "verbs": ["Analyzed", "Modeled", "Forecasted", "Advised", "Managed", "Reconciled", "Audited", "Structured"],
        "metrics": ["managed $X portfolio", "reduced risk by X%", "generated X% return", "saved $X in costs"]
    },
    "marketing": {
        "keywords": ["SEO", "SEM", "Content Strategy", "Google Analytics", "A/B Testing", "CRM", "Email Marketing", "Social Media", "PPC", "ROI", "Funnel"],
        "verbs": ["Launched", "Grew", "Optimized", "Generated", "Converted", "Targeted", "Amplified", "Engaged"],
        "metrics": ["increased traffic X%", "generated X leads", "improved CTR X%", "grew followers X%", "achieved X% conversion"]
    },
    "general": {
        "keywords": ["Leadership", "Project Management", "Communication", "Problem Solving", "Teamwork", "Strategy", "Innovation", "Stakeholder"],
        "verbs": ["Led", "Managed", "Improved", "Created", "Developed", "Implemented", "Coordinated", "Delivered"],
        "metrics": ["increased efficiency X%", "reduced costs X%", "managed team of X", "delivered X projects"]
    }
}

# Weak phrases to replace
WEAK_PHRASES = {
    "responsible for": "Led / Managed / Owned",
    "worked on": "Built / Developed / Engineered",
    "helped with": "Contributed to / Supported",
    "was part of": "Played key role in / Drove",
    "did": "Executed / Delivered / Achieved",
    "made": "Created / Produced / Established",
    "got": "Achieved / Obtained / Secured",
}

def detect_industry(text):
    """Detect which industry the resume targets"""
    scores = {}
    for industry, data in INDUSTRIES.items():
        score = 0
        for kw in data["keywords"]:
            if kw.lower() in text.lower():
                score += 1
        scores[industry] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 2 else "general"

def analyze_resume(text):
    """Analyze a resume and return improvement suggestions"""
    industry = detect_industry(text)
    ind_data = INDUSTRIES[industry]
    
    analysis = {
        "industry": industry,
        "score": 0,
        "word_count": len(text.split()),
        "suggestions": [],
        "keyword_matches": [],
        "weak_phrases_found": [],
    }
    
    # Check for weak phrases
    for weak, strong in WEAK_PHRASES.items():
        if weak.lower() in text.lower():
            analysis["weak_phrases_found"].append({"weak": weak, "suggestion": strong})
    
    # Check keyword coverage
    matched = []
    missing = []
    for kw in ind_data["keywords"]:
        if kw.lower() in text.lower():
            matched.append(kw)
        else:
            missing.append(kw)
    analysis["keyword_matches"] = matched[:10]
    
    # Scoring
    score = 50  # baseline
    
    # Length check
    wc = analysis["word_count"]
    if 300 <= wc <= 800:
        score += 10
        analysis["suggestions"].append("✅ 长度适中 (300-800字)")
    elif wc < 300:
        analysis["suggestions"].append("❌ 内容太少，建议扩充到300字以上")
    else:
        analysis["suggestions"].append("⚠️ 内容较多，压缩到800字以内")
    
    # Keyword check
    kw_pct = len(matched) / max(len(ind_data["keywords"]), 1)
    if kw_pct > 0.5:
        score += 15
        analysis["suggestions"].append(f"✅ 关键词覆盖良好 ({len(matched)}个)")
    else:
        score += 5
        analysis["suggestions"].append(f"⚠️ 缺少行业关键词: {', '.join(missing[:5])}")
    
    # Weak phrases
    if len(analysis["weak_phrases_found"]) == 0:
        score += 15
        analysis["suggestions"].append("✅ 未发现弱动词")
    else:
        analysis["suggestions"].append(f"⚠️ 发现{len(analysis['weak_phrases_found'])}个弱动词需替换")
    
    # Metric check
    has_metrics = bool(re.search(r'\d+%|\$\d+|\d+x|\d+ users|\d+ projects', text))
    if has_metrics:
        score += 10
        analysis["suggestions"].append("✅ 包含量化成果")
    else:
        analysis["suggestions"].append("⚠️ 缺少量化指标，建议添加具体数字")
    
    analysis["score"] = min(score, 95)
    
    return analysis

def optimize_resume(text, industry=None):
    """Optimize a resume based on analysis"""
    if industry is None:
        industry = detect_industry(text)
    
    ind_data = INDUSTRIES.get(industry, INDUSTRIES["general"])
    
    # Replace weak phrases
    result = text
    for weak, strong in WEAK_PHRASES.items():
        pattern = re.compile(r'(?i)\b' + weak + r'\b')
        matches = pattern.findall(result)
        if matches:
            # Only replace first occurrence, suggest others
            result = pattern.sub(strong.split("/")[0].strip(), result, count=1)
    
    # Add keyword suggestions if missing
    analysis = analyze_resume(result)
    
    return {
        "optimized_text": result,
        "industry": industry,
        "suggested_keywords": [k for k in ind_data["keywords"] if k.lower() not in result.lower()][:5],
        "suggested_metrics": ind_data["metrics"][:3],
        "score_before": analyze_resume(text)["score"],
        "score_after": analysis["score"],
    }

def format_resume(name, email, sections):
    """Format resume as clean markdown"""
    md = f"""# {name}

**{email}** | *Generated by AI Resume Optimizer*

---

"""
    for title, content in sections.items():
        md += f"## {title}\n\n{content}\n\n"
    
    md += "---\n\n*Optimized by AI Resume Optimizer — [Get Yours](https://paypal.me/ulnit/5)*"
    return md

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        sample = """
I am responsible for managing a team of 5 developers. 
I worked on several Python projects and helped with deployment.
I was part of the cloud migration team and did some optimization work.
I made improvements to the API and got better response times.
        """
        print("=" * 60)
        print("📝 AI Resume Optimizer — Demo")
        print("=" * 60)
        print("\n📄 ORIGINAL:")
        print(sample)
        print("\n🔍 ANALYSIS:")
        analysis = analyze_resume(sample)
        print(f"  Industry: {analysis['industry']}")
        print(f"  Score: {analysis['score']}/95")
        print(f"  Words: {analysis['word_count']}")
        for s in analysis["suggestions"]:
            print(f"  {s}")
        print(f"\n🔑 Keywords found: {', '.join(analysis['keyword_matches'][:8])}")
        if analysis["weak_phrases_found"]:
            print("⚠️ Weak phrases:")
            for wp in analysis["weak_phrases_found"]:
                print(f"  '{wp['weak']}' → {wp['suggestion']}")
        
        print("\n✨ OPTIMIZED:")
        result = optimize_resume(sample)
        print(result["optimized_text"])
        print(f"\n📊 Score: {result['score_before']} → {result['score_after']}")
        print(f"💡 Add keywords: {', '.join(result['suggested_keywords'])}")
    else:
        print("AI Resume Optimizer v1.0")
        print("Usage: python3 engine.py --demo")
        print("\nPricing:")
        print("  Free: Analysis only")
        print("  Pro $5: Full optimization + formatting")
        print("  VIP $15: Pro + industry tailoring + ATS check")
