import gradio as gr
import importlib.util

# Import the Alysa feedback model
spec_alysa = importlib.util.spec_from_file_location("feedback_model_alysa", "/Users/fadil/repo/ai/capstone/alysa-engine/feedback-model-alysa.py")
feedback_model_alysa = importlib.util.module_from_spec(spec_alysa)
spec_alysa.loader.exec_module(feedback_model_alysa)
ai_toefl_feedback_alysa = feedback_model_alysa.ai_toefl_feedback

# Import the Gemini feedback model
spec_gemini = importlib.util.spec_from_file_location("feedback_model_gemini", "/Users/fadil/repo/ai/capstone/alysa-engine/feedback-model-gemini.py")
feedback_model_gemini = importlib.util.module_from_spec(spec_gemini)
spec_gemini.loader.exec_module(feedback_model_gemini)
ai_toefl_feedback_gemini = feedback_model_gemini.ai_toefl_feedback

def analyze_text(essay_text, model_choice):
    """
    Analyze the input text using selected AI TOEFL feedback model
    """
    if not essay_text or not essay_text.strip():
        return "Please enter some text to analyze.", "", "", "", ""
    
    try:
        # Select the appropriate model
        if model_choice == "Alysa Model (LanguageTool + Transformers)":
            result = ai_toefl_feedback_alysa(essay_text)
            model_info = "**Model Used: Alysa** (LanguageTool + Sentence Transformers)"
        elif model_choice == "Gemini Model (Google AI 2.0 Flash)":
            result = ai_toefl_feedback_gemini(essay_text)
            model_info = "**Model Used: Gemini 2.0 Flash** (Fully Dynamic AI Analysis)"
        else:
            # Default to Alysa
            result = ai_toefl_feedback_alysa(essay_text)
            model_info = "**Model Used: Alysa** (Default)"
        
        # Format the results for display
        score_display = f"{model_info}\n\n**Overall Score: {result['score']}/5.0**"
        
        # Format grammar analysis
        grammar_info = f"**Grammar Errors Found: {result['grammar_errors']}**\n\n"
        if result['detailed_corrections']:
            grammar_info += "**Detailed Corrections:**\n"
            for i, correction in enumerate(result['detailed_corrections'], 1):
                grammar_info += f"{i}. **Error:** `{correction['error_text']}`\n"
                if correction['suggestion']:
                    grammar_info += f"   **Suggestion:** `{correction['suggestion']}`\n"
                grammar_info += f"   **Message:** {correction['message']}\n\n"
        else:
            grammar_info += "No grammar errors detected! ✅"
        
        # Format coherence info
        coherence_info = f"**Coherence Score: {result['avg_coherence']} ({result['avg_coherence']*100:.1f}%)**\n\n"
        coherence_info += "Coherence measures how well your sentences connect to each other."
        
        # Format feedback messages
        feedback_messages = "**AI Feedback:**\n\n"
        for i, message in enumerate(result['feedback'], 1):
            feedback_messages += f"{i}. {message}\n\n"
        
        # Format comparison
        comparison = f"**Original Text:**\n{result['original']}\n\n"
        comparison += f"**AI Corrected Version:**\n{result['corrected']}"
        
        return score_display, grammar_info, coherence_info, feedback_messages, comparison
        
    except Exception as e:
        error_msg = f"Error analyzing text: {str(e)}"
        return error_msg, "", "", "", ""

def get_sample_text(sample_type):
    """
    Return sample texts for testing
    """
    samples = {
        "Good Example": """
        I strongly agree that studying abroad provides valuable opportunities for personal and academic growth. 
        First, living in a foreign country helps students develop independence and cultural awareness. 
        For example, when I studied in Canada, I learned to manage my finances and navigate different social customs. 
        Second, international education offers access to advanced research facilities and diverse perspectives. 
        Therefore, despite the challenges of homesickness and language barriers, studying abroad is a worthwhile investment in one's future.
        """,
        
        "Grammar Errors": """
        Many students want study abroad because they believe it give them more opportunity. 
        Studying in another country help them learn different culture and language. 
        But sometimes they feel lonely and hard to adapt new environment. 
        In my view, studying abroad is good experience if student prepare well before go.
        """,
        
        "Poor Coherence": """
        I like pizza. Education is important. My friend has a car. 
        Students should study hard. The weather is nice today. 
        Technology changes everything. Books are expensive. 
        Learning English is difficult but necessary for success.
        """
    }
    
    return samples.get(sample_type, "")

# Create the Gradio interface
with gr.Blocks(title="TOEFL iBT AI Feedback Analyzer", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # 🎯 TOEFL iBT AI Feedback Analyzer
    
    Test your writing with our AI-powered feedback system that analyzes:
    - **Grammar & Language Use** 📝
    - **Coherence & Organization** 🔗  
    - **Overall TOEFL Scoring** 📊
    
    **Choose your AI model and enter your text below!**
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # Input section
            gr.Markdown("## ✍️ Your Text Input")
            
            # Model selection
            model_dropdown = gr.Dropdown(
                choices=["Alysa Model (LanguageTool + Transformers)", "Gemini Model (Google AI 2.0 Flash)"],
                label="🤖 Choose AI Model",
                value="Alysa Model (LanguageTool + Transformers)",
                info="Alysa: Rule-based analysis | Gemini: Fully dynamic AI analysis"
            )
            
            # Sample text selector
            sample_dropdown = gr.Dropdown(
                choices=["Select a sample...", "Good Example", "Grammar Errors", "Poor Coherence"],
                label="📝 Try Sample Texts",
                value="Select a sample..."
            )
            
            # Main text input
            text_input = gr.Textbox(
                label="Enter your essay or response here:",
                placeholder="Type or paste your TOEFL writing response here...",
                lines=8,
                max_lines=15
            )
            
            # Analyze button
            analyze_btn = gr.Button("🤖 Analyze with AI", variant="primary", size="lg")
            
            # Clear button
            clear_btn = gr.Button("🗑️ Clear", variant="secondary")
        
        with gr.Column(scale=3):
            # Results section
            gr.Markdown("## 📊 Analysis Results")
            
            # Score display
            score_output = gr.Markdown(label="Overall Score")
            
            # Tabbed results
            with gr.Tabs():
                with gr.Tab("📝 Grammar Analysis"):
                    grammar_output = gr.Markdown()
                
                with gr.Tab("🔗 Coherence Analysis"):
                    coherence_output = gr.Markdown()
                
                with gr.Tab("💬 AI Feedback"):
                    feedback_output = gr.Markdown()
                
                with gr.Tab("📋 Text Comparison"):
                    comparison_output = gr.Markdown()
    
    # Event handlers
    def load_sample(sample_type):
        if sample_type == "Select a sample...":
            return ""
        return get_sample_text(sample_type)
    
    def clear_all():
        return "", "", "", "", "", "Select a sample...", "Alysa Model (LanguageTool + Transformers)"
    
    # Connect the events
    sample_dropdown.change(
        fn=load_sample,
        inputs=[sample_dropdown],
        outputs=[text_input]
    )
    
    analyze_btn.click(
        fn=analyze_text,
        inputs=[text_input, model_dropdown],
        outputs=[score_output, grammar_output, coherence_output, feedback_output, comparison_output]
    )
    
    clear_btn.click(
        fn=clear_all,
        outputs=[text_input, score_output, grammar_output, coherence_output, feedback_output, comparison_output, sample_dropdown, model_dropdown]
    )
    
    # Footer
    gr.Markdown("""
    ---
    **🤖 Model Comparison:**
    - **Alysa Model**: Rule-based analysis using LanguageTool + Sentence Transformers (Fast, consistent)
    - **Gemini Model**: Fully dynamic AI analysis using Google Gemini 2.0 Flash (Contextual, adaptive)
    
    **🎯 Gemini Features:**
    - **Dynamic Analysis** - No static rules, fully AI-powered
    - **Contextual Corrections** - Specific to your actual text
    - **Smart Scoring** - Adaptive TOEFL scoring based on content
    - **Natural Feedback** - Human-like suggestions and explanations
    
    **💡 Tips for Better Scores:**
    - Use clear topic sentences and transitions
    - Vary your sentence structure  
    - Support your ideas with specific examples
    - Proofread for grammar and spelling errors
    - Stay focused on the main topic
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )
