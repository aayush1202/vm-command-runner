from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def load_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key="AIzaSyABBS4xu7gMtIyB4F92ZIv5YPQBBkzQZXk",
        temperature=0.3
    )

def generate_script(package, current_version, updated_version, os_type):
    llm = load_llm()
    prompt = PromptTemplate(
        input_variables=["package", "current_version", "updated_version", "os_type"],
        template="""
You are a system administrator assistant. Generate a script to update the package '{package}' from version '{current_version}' to version '{updated_version}' on a '{os_type}' system.

Include:
- Any dependencies that need to be updated or installed
- Generate commands for downloading the package from the web if required
- Add commands to remove the old version if necessary
- Provide an output message indicating each step that is executing, and if it succeeded of failed, but don't create a separate function for this
- Include a success of failure message at the end of the script
- Safe commands for automation

Return only the script without explanations.
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    script = chain.run({"package": package, "current_version": current_version, "updated_version": updated_version, "os_type": os_type}).strip()

    output_file = 'upgrade_script.txt'

    with open(output_file, 'w') as f:
        f.write(script)

    return script
