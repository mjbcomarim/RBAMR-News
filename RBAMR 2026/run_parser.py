# -- coding: utf-8 --
import os
from conllu import parse
from modern_amr_parser import ModernAMRParser

def render_amr(nodes, current_var, visited, depth=0):
    if current_var == '-': return "-"
    if isinstance(current_var, str) and current_var.startswith('"'): return current_var
    
    if current_var not in nodes: return current_var
    
    info = nodes[current_var]
    indent = "    " * (depth + 1)
    amr_str = f"({info['var']} / {info['concept']}"
    
    for role, target in info.get('edges', []):
        val = render_amr(nodes, target, visited, depth + 1)
        amr_str += f"\n{indent}{role} {val}"
            
    return amr_str + ")"


if __name__ == "__main__":
    parser = ModernAMRParser()

    input_file = 'entrada.conllu'
    output_file = 'output_amr.txt'

    if os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            sentences = parse(f.read())

        #RESET (se rodar várias vezes)
        parser.reset_support()

##### 100 sentenças
        #with open(output_file, 'w', encoding='utf-8') as f_out:
            # O loop vai parar na centésima sentença
         #   for sent in sentences[:100]: 
         #       res_list = parser.execute([sent])
                # ... resto do código igual ...
        with open(output_file, 'w', encoding='utf-8') as f_out:
           for sent in sentences:
                res_list = parser.execute([sent])

                if not res_list:
                    continue
                
                data = res_list[0]
                nodes = data['nodes']
                root_var = data['root']
                
                f_out.write(f"# ::tok {sent.metadata.get('text', '')}\n")

                if root_var and root_var in nodes:
                    f_out.write(render_amr(nodes, root_var, set()) + "\n\n")
                elif nodes:
                    fallback = list(nodes.keys())[0]
                    f_out.write(render_amr(nodes, fallback, set()) + "\n\n")

        print("Processamento concluído com sucesso!")

        # =========================
        # PRINT DO SUPPORT
        # =========================
        print("\n=== SUPPORT DAS REGRAS ===")

        support = parser.get_support()

        for rule, value in sorted(support.items(), key=lambda x: -x[1]):
            print(f"{rule:20s} {value:.4f}")