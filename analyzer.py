import ast
import litellm


class CodeAnalyzer:
    def __init__(
        self,
        code,
        api_key,
        model,
        provider="openai",
        ollama_base_url="http://localhost:11434",
    ):
        self.code = code
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.ollama_base_url = ollama_base_url

    def get_structure(self, show_internal):
        tree = ast.parse(self.code)
        nodes = []
        edges = []

        for node in ast.walk(tree):
            # 1. Handle Classes
            if isinstance(node, ast.ClassDef):
                nodes.append({
                    "id": node.name,
                    "label": f"Class: {node.name}",
                    "color": "#1C83E1",
                })

                # Look for methods inside the class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Create a UNIQUE ID by combining Class + Method
                        method_id = f"{node.name}.{item.name}"
                        nodes.append({
                            "id": method_id,
                            "label": f"fn: {item.name}",
                            "color": "#FF4B4B",
                        })
                        # Link Method to its Class
                        edges.append({"source": node.name, "target": method_id})

                        # Optional: Look for calls inside methods
                        for child in ast.walk(item):
                            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                                # Link to the called function
                                edges.append({"source": method_id, "target": child.func.id})

            # 2. Handle Global Functions (functions not inside a class)
            if isinstance(node, ast.FunctionDef):
                # Check if this function was already handled as a class method
                # If not, it's a global function
                is_global = not any(node.name in n["id"] for n in nodes if "." in n["id"])

                if is_global:
                    nodes.append({
                        "id": node.name,
                        "label": f"fn: {node.name}",
                        "color": "#FF4B4B",
                    })

        return nodes, edges

    def get_llm_summary(self):
        prompt = f"Explain the architectural pattern of this code briefly: \n\n{self.code}"

        try:
            if self.provider == "ollama":
                model_name = self.model
                if not model_name.startswith("ollama/"):
                    model_name = f"ollama/{model_name}"

                response = litellm.completion(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    api_base=self.ollama_base_url,
                )
                return response.choices[0].message.content

            if not self.api_key:
                return "Enter an API key to get semantic insights."

            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM Error: {str(e)}"
