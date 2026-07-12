import requests

# Apna GitHub username yahan likho
username = "derravi"

# per_page=100 se maximum 100 repos ek baar me milenge
url = f"https://api.github.com/users/{username}/repos?per_page=100"

response = requests.get(url)

if response.status_code == 200:
    repos = response.json()

    print(f"\n📌 Total Repositories of {username}: {len(repos)}\n")

    for index, repo in enumerate(repos, start=1):
        print(f"{index}. {repo['name']}")

else:
    print("❌ Failed to fetch repositories")
    print("Status Code:", response.status_code)


"""
-> Pending projects

-Python-Data-Science-Cheat-Sheets-Basics-of-Pandas-NumPy-Matplotlib- ------------------------------
-Python-Star-Pattern-Collection 
Age-Calculator-GUI-using-Python ------------------------------
AI-Powered_Car_Price_Estimation_and_Market_Segmentation
AI_Notes_Summarizer_with_Ollama_and_Fast_API
Auto-password-genorater
Automated_Customer_Churn_Risk_Prediction_Machine_Learning_System
Bank_Account_Management_API
Creative_Python_Pattern_Printing_Collection
Data-Encoding-Techniques-in-Machine-Learning-Label-OneHot-Ordinal-
demo
Demo-2
Demo_Repo
derravi
DigiShield_Locker_System
Digital_Clock_using_Python_-_Tkinter
Docker-Material-Scratch-to-Advance-with-CheatSheet
Employee_Attrition_Prediction_Using_Machine_Learning_-IBM_HR_Dataset-
Employee_Directory-FastAPI_Pipeline-CRUD_Operations-
End-to-End_Laptop_Price_Prediction_using_Python
FastAPI_Patient_Management_CRUD_Application
FastAPI_Student_Result_Management_System
Fast_APIs_Material
Gmail-Attachment-Downloader-with-Python
HR_Data-Set-Cleaning-and-Preprocessing-with-Pandas-numpy
Inheritance-in-python-
Intelligent_Spam_Detection_System_using_NLP_and_Machine_Learning
jpg_to_pdf_converter
K-Means_Clustering_for_Customer_Segmentation
List_interview-Coding-Programs-Part-1
LocalGPT-Privacy-First_AI_Chat_Assistant_using_Ollama
Machine_learning_Work_Flow
Model-Evaluation-Techniques-in-Machine-Learning-Regression-Classification-Metrics-
MySQL_Practice_Querys
Netflix-Data-Cleaning-with-Pandas-Remove-Null-Values-
Netflix-Demo-Website
Netflix-Website
Nipah_Virus_Early_Risk_Prediction_System_2026
Notes-Website-ToDo-List-
Ola_Case_Study_Data_Analytics
Phone-Number-Information-Extractor-using-Python
Pizza_Sales_Clustering_Analysis
Pydantic_Validation_HandsOn
Python-Built-in-Data-Structures-Functions
Python_basic_Codes
PyTorch_From_Scratch_to_Advanced
QRcode-genorater
Quiz-website-Using-HTML-CSS-JS
Research-Paper-Unintended-Consequences-Investigating-AI-Induced-Fatalities-in-Autonomous-System-
Sample-project-2
Smart-Face-Eye-Smile-Detection-using-OpenCV
SmartPrice-AI-Smartphone-Price-Prediction-System-using-Machine-Learning
Speaker_Diarization_Using_Pyhton
stock-price-prediction-using-ML-and-Django
Student-Data-Cleaning-and-Preprocessing-with-Pandas-numpy
Supervised-Machine-Learning-with-Scikit-Learn
The-Developers-Arena-Intership-Task
Webcam_to_Sketch_In_Python
Yearly-Calendar-Generator-Python-Tkinter
YouTube-Video-Downloader
"""


"""
{% extends 'base.html' %}

{% block title %}Education - Ravi Der{% endblock %}

{% block extra_css %}
<style>
:root {
    --primary: #00f3ff;
    --secondary: #7b00ff;
    --dark: #0a0a1a;
    --darker: #050510;
    --light: #e2f1f8;
    --accent: #ff00c8;
}

html {
    scroll-behavior: smooth;
}

body {
    font-family: 'Exo 2', sans-serif;
    background-color: var(--darker);
    color: var(--light);
    overflow-x: hidden;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
}

.section {
    min-height: 100vh;
    padding-top: 100px;
    position: relative;
}

/* Background Animation */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 15% 50%, rgba(123, 0, 255, 0.1) 0%, transparent 20%),
        radial-gradient(circle at 85% 30%, rgba(0, 243, 255, 0.1) 0%, transparent 20%),
        radial-gradient(circle at 50% 80%, rgba(255, 0, 200, 0.05) 0%, transparent 20%);
    z-index: -1;
}

/* Section Headers */
.section-header {
    position: relative;
    z-index: 2;
    text-align: center;
    margin-bottom: 60px;
    padding: 0 15px;
}

.section-icon {
    font-size: 3rem;
    margin-bottom: 20px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    display: inline-block;
}

.section-title {
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 15px;
    background: linear-gradient(135deg, var(--primary), var(--secondary), var(--accent));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 0 30px rgba(0, 243, 255, 0.3);
    line-height: 1.2;
}

.section-subtitle p {
    font-size: 1.2rem;
    color: rgba(226, 241, 248, 0.7);
    font-weight: 300;
    line-height: 1.6;
}

/* Education Section */
#education {
    background-color: rgba(5, 5, 16, 0.7);
    padding: 40px 0;
}

.education-card {
    background: rgba(10, 10, 26, 0.7);
    border-radius: 20px;
    padding: 35px;
    border: 1px solid rgba(0, 243, 255, 0.1);
    transition: all 0.4s ease;
    height: 100%;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
    margin-bottom: 25px;
}

.education-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(0, 243, 255, 0.05), 
        transparent);
    transition: left 0.6s ease;
}

.education-card:hover::before {
    left: 100%;
}

.education-card:hover {
    transform: translateY(-10px);
    border-color: var(--primary);
    box-shadow: 0 15px 35px rgba(0, 243, 255, 0.2);
}

.education-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 20px;
}

.education-badge {
    position: relative;
    width: 80px;
    height: 80px;
    flex-shrink: 0;
}

.education-icon {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--darker);
    font-size: 2rem;
    border: 2px solid rgba(0, 243, 255, 0.3);
}

.badge-glow {
    position: absolute;
    top: -5px;
    left: -5px;
    right: -5px;
    bottom: -5px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 25px;
    filter: blur(15px);
    opacity: 0.4;
    z-index: -1;
    transition: all 0.3s ease;
}

.education-card:hover .badge-glow {
    opacity: 0.6;
    filter: blur(20px);
}

.education-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
}

.education-date {
    background: rgba(0, 243, 255, 0.1);
    color: var(--primary);
    padding: 6px 15px;
    border-radius: 15px;
    font-size: 0.85rem;
    font-weight: 600;
    border: 1px solid rgba(0, 243, 255, 0.2);
}

.education-type {
    background: rgba(123, 0, 255, 0.1);
    color: var(--secondary);
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    border: 1px solid rgba(123, 0, 255, 0.2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.education-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 8px;
    line-height: 1.3;
}

.education-institution {
    font-size: 1.2rem;
    font-weight: 600;
    color: rgba(226, 241, 248, 0.9);
    margin-bottom: 15px;
}

.education-description {
    color: rgba(226, 241, 248, 0.8);
    line-height: 1.6;
    margin-bottom: 20px;
}

.education-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
}

.detail-item {
    text-align: center;
    padding: 15px;
    background: rgba(0, 243, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(0, 243, 255, 0.1);
    transition: all 0.3s ease;
}

.detail-item:hover {
    background: rgba(0, 243, 255, 0.1);
    transform: translateY(-2px);
}

.detail-value {
    font-size: 1.3rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 5px;
    line-height: 1;
}

.detail-label {
    color: rgba(226, 241, 248, 0.7);
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.education-skills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 25px;
}

.skill-tag {
    background: rgba(255, 0, 200, 0.1);
    color: var(--accent);
    padding: 6px 12px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    border: 1px solid rgba(255, 0, 200, 0.2);
    transition: all 0.3s ease;
}

.skill-tag:hover {
    background: rgba(255, 0, 200, 0.2);
    transform: translateY(-2px);
}

.certificate-link {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: var(--darker);
    text-decoration: none;
    padding: 10px 20px;
    border-radius: 25px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}

.certificate-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 243, 255, 0.4);
    color: var(--darker);
}

/* Courses Section */
.courses-section {
    margin-top: 80px;
    padding: 0 15px;
}

.course-card {
    background: rgba(10, 10, 26, 0.6);
    border: 1px solid rgba(0, 243, 255, 0.1);
    border-radius: 15px;
    padding: 25px;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
    height: 100%;
    margin-bottom: 25px;
}

.course-card:hover {
    border-color: var(--primary);
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 243, 255, 0.15);
}

.course-provider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
}

.provider-logo {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--darker);
    font-size: 1.2rem;
    flex-shrink: 0;
}

.provider-name {
    font-size: 0.9rem;
    color: var(--primary);
    font-weight: 600;
}

.course-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--light);
    margin-bottom: 10px;
    line-height: 1.4;
}

.course-duration {
    color: rgba(226, 241, 248, 0.7);
    font-size: 0.8rem;
    margin-bottom: 15px;
}

.course-skills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.course-skill {
    background: rgba(0, 243, 255, 0.1);
    color: var(--primary);
    padding: 4px 8px;
    border-radius: 8px;
    font-size: 0.7rem;
    font-weight: 500;
    border: 1px solid rgba(0, 243, 255, 0.2);
    transition: all 0.3s ease;
}

.course-skill:hover {
    background: rgba(0, 243, 255, 0.2);
}

/* ========== RESPONSIVE DESIGN ========== */

/* Large Desktop */
@media (min-width: 1200px) {
    .section-title {
        font-size: 3rem;
    }
    
    .education-card {
        padding: 40px;
    }
    
    .education-details {
        grid-template-columns: repeat(3, 1fr);
    }
}

/* Desktop */
@media (min-width: 992px) and (max-width: 1199px) {
    .section-title {
        font-size: 2.6rem;
    }
    
    .education-card {
        padding: 30px;
    }
    
    .education-details {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Tablet Landscape */
@media (min-width: 768px) and (max-width: 991px) {
    .section {
        padding-top: 80px;
        min-height: auto;
    }
    
    .section-title {
        font-size: 2.4rem;
    }
    
    .section-subtitle p {
        font-size: 1.1rem;
    }
    
    .education-card {
        padding: 30px;
        border-radius: 18px;
    }
    
    .education-header {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;
    }
    
    .education-meta {
        align-items: flex-start;
    }
    
    .education-badge {
        width: 70px;
        height: 70px;
    }
    
    .education-icon {
        font-size: 1.8rem;
    }
    
    .education-title {
        font-size: 1.4rem;
    }
    
    .education-institution {
        font-size: 1.1rem;
    }
    
    .education-details {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    
    .detail-item {
        padding: 12px;
    }
    
    .detail-value {
        font-size: 1.2rem;
    }
    
    .course-card {
        padding: 20px;
    }
    
    .course-title {
        font-size: 1rem;
    }
}

/* Tablet Portrait */
@media (min-width: 576px) and (max-width: 767px) {
    .section {
        padding-top: 70px;
        min-height: auto;
    }
    
    .section-header {
        margin-bottom: 40px;
    }
    
    .section-title {
        font-size: 2.2rem;
    }
    
    .section-subtitle p {
        font-size: 1.1rem;
    }
    
    .section-icon {
        font-size: 2.5rem;
    }
    
    .education-card {
        padding: 25px;
        border-radius: 16px;
        margin-bottom: 20px;
    }
    
    .education-header {
        flex-direction: row;
        align-items: flex-start;
        gap: 15px;
    }
    
    .education-badge {
        width: 60px;
        height: 60px;
    }
    
    .education-icon {
        font-size: 1.6rem;
        border-radius: 15px;
    }
    
    .education-meta {
        align-items: flex-end;
    }
    
    .education-date {
        font-size: 0.8rem;
        padding: 5px 12px;
    }
    
    .education-type {
        font-size: 0.7rem;
        padding: 3px 10px;
    }
    
    .education-title {
        font-size: 1.3rem;
    }
    
    .education-institution {
        font-size: 1.1rem;
    }
    
    .education-description {
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .education-details {
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .detail-item {
        padding: 12px 8px;
    }
    
    .detail-value {
        font-size: 1.1rem;
    }
    
    .detail-label {
        font-size: 0.75rem;
    }
    
    .education-skills {
        gap: 6px;
        margin-bottom: 20px;
    }
    
    .skill-tag {
        font-size: 0.7rem;
        padding: 5px 10px;
    }
    
    .courses-section {
        margin-top: 60px;
    }
    
    .course-card {
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .course-title {
        font-size: 1rem;
    }
    
    .provider-logo {
        width: 35px;
        height: 35px;
        font-size: 1rem;
    }
}

/* Mobile Devices */
@media (max-width: 575px) {
    .section {
        padding-top: 60px;
        min-height: auto;
    }
    
    .section-header {
        margin-bottom: 30px;
        padding: 0 10px;
    }
    
    .section-title {
        font-size: 1.8rem;
        margin-bottom: 10px;
    }
    
    .section-subtitle p {
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .section-icon {
        font-size: 2.2rem;
        margin-bottom: 15px;
    }
    
    .education-card {
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 20px;
    }
    
    .education-header {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;
        margin-bottom: 15px;
    }
    
    .education-badge {
        width: 55px;
        height: 55px;
    }
    
    .education-icon {
        font-size: 1.4rem;
        border-radius: 12px;
    }
    
    .education-meta {
        align-items: flex-start;
        gap: 6px;
    }
    
    .education-date {
        font-size: 0.75rem;
        padding: 4px 10px;
    }
    
    .education-type {
        font-size: 0.65rem;
        padding: 3px 8px;
    }
    
    .education-title {
        font-size: 1.2rem;
        margin-bottom: 6px;
    }
    
    .education-institution {
        font-size: 1rem;
        margin-bottom: 12px;
    }
    
    .education-description {
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 15px;
    }
    
    .education-details {
        grid-template-columns: 1fr;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .detail-item {
        padding: 12px 10px;
    }
    
    .detail-value {
        font-size: 1.1rem;
    }
    
    .detail-label {
        font-size: 0.75rem;
    }
    
    .education-skills {
        gap: 5px;
        margin-bottom: 15px;
    }
    
    .skill-tag {
        font-size: 0.65rem;
        padding: 4px 8px;
        border-radius: 10px;
    }
    
    .certificate-link {
        padding: 8px 16px;
        font-size: 0.85rem;
        width: 100%;
        justify-content: center;
    }
    
    .courses-section {
        margin-top: 40px;
        padding: 0 10px;
    }
    
    .course-card {
        padding: 18px;
        margin-bottom: 15px;
        border-radius: 12px;
    }
    
    .course-provider {
        margin-bottom: 12px;
    }
    
    .provider-logo {
        width: 32px;
        height: 32px;
        font-size: 0.9rem;
        border-radius: 8px;
    }
    
    .provider-name {
        font-size: 0.8rem;
    }
    
    .course-title {
        font-size: 0.95rem;
        margin-bottom: 8px;
    }
    
    .course-duration {
        font-size: 0.75rem;
        margin-bottom: 12px;
    }
    
    .course-skills {
        gap: 4px;
    }
    
    .course-skill {
        font-size: 0.65rem;
        padding: 3px 6px;
    }
    
    .container {
        padding: 0 15px;
    }
}

/* Small Mobile Devices */
@media (max-width: 375px) {
    .section-title {
        font-size: 1.6rem;
    }
    
    .section-subtitle p {
        font-size: 0.95rem;
    }
    
    .education-card {
        padding: 18px 15px;
    }
    
    .education-title {
        font-size: 1.1rem;
    }
    
    .education-institution {
        font-size: 0.95rem;
    }
    
    .education-description {
        font-size: 0.85rem;
    }
    
    .detail-value {
        font-size: 1rem;
    }
    
    .skill-tag {
        font-size: 0.6rem;
        padding: 3px 6px;
    }
    
    .course-card {
        padding: 15px;
    }
    
    .course-title {
        font-size: 0.9rem;
    }
}

/* Landscape Orientation for Mobile */
@media (max-height: 500px) and (max-width: 768px) {
    .section {
        padding-top: 50px;
        min-height: auto;
    }
    
    .education-card {
        padding: 20px;
    }
    
    .education-header {
        flex-direction: row;
        gap: 15px;
    }
    
    .education-badge {
        width: 50px;
        height: 50px;
    }
    
    .education-icon {
        font-size: 1.2rem;
    }
}

/* High-resolution displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    .education-card {
        border-width: 1.5px;
    }
    
    .badge-glow {
        filter: blur(12px);
    }
}

/* Print Styles */
@media print {
    .education-card:hover,
    .course-card:hover {
        transform: none !important;
        box-shadow: none !important;
    }
    
    .badge-glow {
        display: none;
    }
}

/* Reduced motion for accessibility */
@media (prefers-reduced-motion: reduce) {
    .education-card,
    .course-card,
    .detail-item,
    .skill-tag {
        transition: none !important;
    }
    
    .education-card::before {
        display: none;
    }
    
    html {
        scroll-behavior: auto;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .education-card,
    .course-card {
        background: rgba(0, 0, 0, 0.4);
    }
}

/* Touch device optimizations */
@media (hover: none) {
    .education-card:hover {
        transform: none;
        box-shadow: 0 5px 15px rgba(0, 243, 255, 0.1);
    }
    
    .detail-item:hover,
    .skill-tag:hover,
    .course-skill:hover {
        transform: none;
    }
    
    .certificate-link:hover {
        transform: none;
        box-shadow: none;
    }
}

</style>
{% endblock %}

{% block content %}
<!-- Education Section -->
<section id="education" class="section">
    <div class="container">
        <div class="section-header">
            <div class="section-icon">
                <i class="fas fa-graduation-cap"></i>
            </div>
            <h2 class="section-title">Education & Learning</h2>
            <div class="section-subtitle">
                <p>Academic journey and continuous learning path</p>
            </div>
        </div>

        <div class="row">
            <!-- Current Education -->
            <div class="col-lg-6">
                <div class="education-card">
                    <div class="education-header">
                        <div class="education-badge">
                            <div class="education-icon">
                                <i class="fas fa-university"></i>
                            </div>
                            <div class="badge-glow"></div>
                        </div>
                        <div class="education-meta">
                            <span class="education-date">2025 - Present</span>
                            <span class="education-type">Postgraduate</span>
                        </div>
                    </div>

                    <h3 class="education-title">M.Tech in Ai/ML & Data Science</h3>
                    <h4 class="education-institution">Gyanmanjari Innovative University , Bhavnagar</h4>
                    
                    <p class="education-description">
                        Pursuing an advanced postgraduate program where I'm learning AI/ML, Natural Language Processing (NLP), OpenCV, Neural Networks, and Advanced Mathematics to build intelligent and data-driven solutions.
                    </p>

                    <div class="education-details">
                        <div class="detail-item">
                            <div class="detail-value">CGPA: </div>
                            <div class="detail-label">Current GPA</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-value">O+</div>
                            <div class="detail-label">AI/ML & Data Science</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-value">--</div>
                            <div class="detail-label">Attendance</div>
                        </div>
                    </div>

                    <div class="education-skills">
                        <span class="skill-tag">Artificial Intelligence</span>
                        <span class="skill-tag">Machine Learning</span>
                        <span class="skill-tag">Deep Learning</span>
                        <span class="skill-tag">NLP</span>
                        <span class="skill-tag">Neural Networks</span>
                        <span class="skill-tag">Data Mining</span>
                        <span class="skill-tag">Big Data</span>
                        <span class="skill-tag">Computer Vision</span>
                    </div>
                </div>
            </div>

            <!-- Previous Education -->
            <div class="col-lg-6">
                <div class="education-card">
                    <div class="education-header">
                        <div class="education-badge">
                            <div class="education-icon">
                                <i class="fas fa-graduation-cap"></i>
                            </div>
                            <div class="badge-glow"></div>
                        </div>
                        <div class="education-meta">
                            <span class="education-date">2021 - 2025</span>
                            <span class="education-type">Graduate</span>
                        </div>
                    </div>

                    <h3 class="education-title">B.Tech in Information Technology</h3>
                    <h4 class="education-institution">Atmiya University, Rajkot</h4>
                    
                    <p class="education-description">
                        Completed a comprehensive undergraduate program focusing on software engineering, database systems, web technologies, and computer fundamentals, gaining strong technical skills and academic excellence.</p>

                    <div class="education-details">
                        <div class="detail-item">
                            <div class="detail-value">8.90/10</div>
                            <div class="detail-label">Final CGPA</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-value">10/10</div>
                            <div class="detail-label">Final SGPA</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-value">2</div>
                            <div class="detail-label">Internships</div>
                        </div>
                    </div>

                    <div class="education-skills">
                        <span class="skill-tag">Python</span>
                        <span class="skill-tag">C/C++</span>
                        <span class="skill-tag">Web Development</span>
                        <span class="skill-tag">OOPS Concepts</span>
                        <span class="skill-tag">Data Structures</span>
                    </div>
                </div>
            </div>

            <div class="col-lg-6">
                <div class="education-card">
                    <div class="education-header">
                        <div class="education-badge">
                            <div class="education-icon">
                                <i class="fas fa-graduation-cap"></i>
                            </div>
                            <div class="badge-glow"></div>
                        </div>
                        <div class="education-meta">
                            <span class="education-date">2021 - 2022</span>
                            <span class="education-type">12th - Science</span>
                        </div>
                    </div>

                    <h3 class="education-title">12th - SCIENCE- A-Group , GSEB </h3>
                    <h4 class="education-institution">Gujarat Board</h4>
                    
                    <p class="education-description">
                        I Am completed my 12th Science Higher Secondary School Certificate, Gujarat Board, from Shree U.M Ajmera Higher Secondary School, Damnagar.</p>

                    <div class="education-details">
                        <div class="detail-item">
                            <div class="detail-value">62.63%</div>
                            <div class="detail-label">Percentage</div>
                        </div>
                    </div>

                    <div class="education-skills">
                        <span class="skill-tag">Maths</span>
                        <span class="skill-tag">Physics</span>
                        <span class="skill-tag">Chemistry</span>
                    </div>
                </div>
            </div>

            <div class="col-lg-6">
                <div class="education-card">
                    <div class="education-header">
                        <div class="education-badge">
                            <div class="education-icon">
                                <i class="fas fa-graduation-cap"></i>
                            </div>
                            <div class="badge-glow"></div>
                        </div>
                        <div class="education-meta">
                            <span class="education-date">2019 - 2020</span>
                            <span class="education-type">10Th</span>
                        </div>
                    </div>

                    <h3 class="education-title">10Th </h3>
                    <h4 class="education-institution">Gujarat Board</h4>
                    
                    <p class="education-description">
                        I Am completed my 10th Secondary School Certificate Gujarat Board, from Shree Swaminarayan Gurukul, Damnagar.</p>

                    <div class="education-details">
                        <div class="detail-item">
                            <div class="detail-value">60.81%</div>
                            <div class="detail-label">Percentage</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}

{% block extra_js %}
<script>
// Education page specific animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate education cards on scroll
    const educationCards = document.querySelectorAll('.education-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                // Animate detail items with staggered delay
                const detailItems = entry.target.querySelectorAll('.detail-item');
                detailItems.forEach((item, index) => {
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'scale(1)';
                    }, index * 100 + 300);
                });
                
                // Animate skill tags with staggered delay
                const skillTags = entry.target.querySelectorAll('.skill-tag');
                skillTags.forEach((tag, index) => {
                    setTimeout(() => {
                        tag.style.opacity = '1';
                        tag.style.transform = 'translateY(0)';
                    }, index * 50 + 500);
                });
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Set initial states and observe
    educationCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        
        // Set initial states for detail items and skill tags
        const detailItems = card.querySelectorAll('.detail-item');
        const skillTags = card.querySelectorAll('.skill-tag');
        
        detailItems.forEach(item => {
            item.style.opacity = '0';
            item.style.transform = 'scale(0.8)';
            item.style.transition = 'all 0.4s ease';
        });
        
        skillTags.forEach(tag => {
            tag.style.opacity = '0';
            tag.style.transform = 'translateY(10px)';
            tag.style.transition = 'all 0.3s ease';
        });
        
        observer.observe(card);
    });

    // Add hover effects only for non-touch devices
    if (window.matchMedia("(hover: hover)").matches) {
        educationCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-15px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(-10px) scale(1)';
            });
        });
    }

    // Add click effects to certificate links
    const certificateLinks = document.querySelectorAll('.certificate-link');
    certificateLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
                // Simulate opening certificate
                alert('Certificate would open in new tab');
            }, 150);
        });
    });
});

// Touch device optimizations
if ('ontouchstart' in window) {
    // Add touch feedback for education cards
    const educationCards = document.querySelectorAll('.education-card');
    educationCards.forEach(card => {
        card.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        card.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Make skill tags more touch-friendly
    const skillTags = document.querySelectorAll('.skill-tag');
    skillTags.forEach(tag => {
        tag.style.padding = '8px 12px';
    });
}
</script>
{% endblock %}
"""