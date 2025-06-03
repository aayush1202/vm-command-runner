from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def load_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key="AIzaSyABBS4xu7gMtIyB4F92ZIv5YPQBBkzQZXk",
        temperature=0.3
    )

def generate_script(package, updated_version, os_type):
    llm = load_llm()
    prompt = PromptTemplate(
        input_variables=["package", "updated_version", "os_type"],
        template="""
You are a system administrator assistant. Generate a PowerShell script to update the package '{package}' to version '{updated_version}' on a Windows system.

Requirements:
- Assume that the script is being run with administrator access.
- Do not make any custom functions. 
- Generate commands to download the package from the web, and install it. 
- Add the installation directory to the system PATH environment variable (if it isn't already present).
- The script will be run using Azure Run Command on a Windows VM. 
- Verify installation by checking the version of the package at the end. 

Return only the PowerShell script with no explanations or markdown.
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    script = chain.run({"package": package, "updated_version": updated_version, "os_type": os_type}).strip()

    output_file = '../generated_scripts/upgrade_script_windows.txt'

    with open(output_file, 'w') as f:
        f.write(script)

    return script
