import ast
import litellm
from radon.complexity import cc_visit


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

    @staticmethod
    def _health_color(score):
        if score is None:
            return "#9CA3AF"
        if score <= 5:
            return "#00FFA3"
        if score <= 10:
            return "#FFD700"
        return "#FF4B4B"

    @staticmethod
    def _call_name(call_node):
        func = call_node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            parts = []
            current = func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return None

    def _complexity_by_symbol(self):
        metrics = {}
        try:
            blocks = cc_visit(self.code)
        except Exception:
            return metrics

        for block in blocks:
            name = getattr(block, "name", None)
            if not name:
                continue

            complexity = getattr(block, "complexity", None)
            classname = getattr(block, "classname", None)
            if classname:
                metrics[f"{classname}.{name}"] = complexity
            else:
                metrics[name] = complexity

        return metrics

    def get_structure(self, show_internal):
        tree = ast.parse(self.code)
        complexity_map = self._complexity_by_symbol()
        nodes = []
        edges = []
        known_nodes = set()

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                if node.name not in known_nodes:
                    nodes.append({
                        "id": node.name,
                        "label": f"Class: {node.name}",
                        "color": "#1C83E1",
                        "cc_score": None,
                        "title": f"Class: {node.name}",
                    })
                    known_nodes.add(node.name)

                for item in node.body:
                    if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue

                    method_id = f"{node.name}.{item.name}"
                    cc_score = complexity_map.get(method_id)
                    cc_color = self._health_color(cc_score)
                    cc_display = cc_score if cc_score is not None else "N/A"
                    nodes.append({
                        "id": method_id,
                        "label": f"fn: {item.name}",
                        "color": cc_color,
                        "cc_score": cc_score,
                        "title": f"fn: {item.name}\nCyclomatic Complexity: {cc_display}",
                    })
                    known_nodes.add(method_id)
                    edges.append({"source": node.name, "target": method_id})

                    for child in ast.walk(item):
                        if isinstance(child, ast.Call):
                            call_name = self._call_name(child)
                            if call_name:
                                edges.append({"source": method_id, "target": call_name})

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                cc_score = complexity_map.get(node.name)
                cc_color = self._health_color(cc_score)
                cc_display = cc_score if cc_score is not None else "N/A"
                nodes.append({
                    "id": node.name,
                    "label": f"fn: {node.name}",
                    "color": cc_color,
                    "cc_score": cc_score,
                    "title": f"fn: {node.name}\nCyclomatic Complexity: {cc_display}",
                })
                known_nodes.add(node.name)
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        call_name = self._call_name(child)
                        if call_name:
                            edges.append({"source": node.name, "target": call_name})

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
