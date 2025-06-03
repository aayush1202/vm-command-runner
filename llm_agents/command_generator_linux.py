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
You are a system administrator assistant. Generate a script to update the package '{package}' to version '{updated_version}' on a '{os_type}' system. There would be a version of the package already installed in the system.

Requirements:
- Use POSIX-compliant shell syntax (use `[ ]` instead of `[[ ]]`, avoid bash-only features).
- Assume that the package is not present in the default repositories.
- Remove the current package if necessary.
- Manually install the package from the web.
- Use parallelized commands where possible, like 'make -j "$(nproc)"'.
- Ensure the script works under /bin/sh, compatible with Azure VM Run Command.
- Do not create custom functions.
- install to /user/local/bin if possible.
- Do not use sudo, assume the script is run as root.

Return only the shell script with no explanations or markdown.
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    script = chain.run({"package": package, "updated_version": updated_version, "os_type": os_type}).strip()

    output_file = '../generated_scripts/upgrade_script_linux.txt'

    with open(output_file, 'w') as f:
        f.write(script)

    return script
