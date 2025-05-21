from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def load_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key="AIzaSyABBS4xu7gMtIyB4F92ZIv5YPQBBkzQZXk",
        temperature=0.3
    )

def generate_revert_script(original_script: str):
    
    llm = load_llm()
    prompt = PromptTemplate(
        input_variables=["original_script"],
        template="""
You are a system administrator assistant. A user has run the following shell script on a Linux system:

{original_script}

Generate a *revert* or *rollback* shell script that undoes the changes made by the above script.
- If packages were installed, uninstall them, and revert to the previous version.
- If packages were removed, reinstall them and their dependencies. 
- If files were downloaded or modified, remove or revert them.
- Make sure the rollback is safe to run.

Return only the shell script without any explanation.
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    revert_script = chain.run({"original_script": original_script}).strip()

    output_file="revert_script.txt"
    # Write revert script to file
    with open(output_file, "w") as f:
        f.write(revert_script)

    return revert_script
