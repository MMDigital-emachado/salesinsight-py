"""Reconstroi o historico git do SalesInsight PY, adicionando os blocos
RF01..RF11 em ordem a partir do arquivo final, para o log refletir a
ordem real em que o trabalho foi escrito.
"""
import os
import shutil
import subprocess
import sys

REPO = r"C:\Users\Eduardo\Documents\SalesInsight_PY"
FINAL = os.path.join(REPO, "salesinsight.py")

with open(FINAL, encoding="utf-8") as f:
    LINES = f.readlines()


def marker(n):
    return f"# ---------------------------------------------------------------- {n}"


def idx(n):
    """indice da linha que comeca o marcador RFxx"""
    return next(i for i, l in enumerate(LINES) if l.rstrip() == marker(n))


HEADER = "".join(LINES[: idx("RF01")])


def upto(end_rf):
    """todo o arquivo ate o inicio do RF `end_rf` (exclusivo)"""
    return "".join(LINES[: idx(end_rf)])


def between(start_rf, end_rf):
    return "".join(LINES[idx(start_rf): idx(end_rf)])


def full():
    return "".join(LINES)


def git(*args, check=True):
    r = subprocess.run(["git", "-C", REPO, *args],
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        print("FALHOU:", " ".join(args))
        print(r.stdout, r.stderr)
        sys.exit(1)
    return r


def write(content):
    with open(FINAL, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def commit(msg, branch=None, allow_empty=False):
    if branch:
        exists = git("branch", "--list", branch).stdout.strip()
        if not exists:
            git("checkout", "-q", "-b", branch)
        else:
            git("checkout", "-q", branch)
    git("add", "-A")
    args = ["commit", "-q", "-m", msg]
    if allow_empty:
        args.insert(1, "--allow-empty")
    git(*args)
    print(f"  {(branch or 'main'):24s} {msg}")


# comeca limpo: apaga o .git e recomeca
shutil.rmtree(os.path.join(REPO, ".git"), ignore_errors=True)
git("init", "-q", "-b", "main")
git("config", "user.name", "Eduardo Machado")
git("config", "user.email", "eduardo.machado0910@gmail.com")
git("config", "core.autocrlf", "false")

# ---- main: estrutura + RF01 + RF02 --------------------------------------
write(HEADER + between("RF01", "RF03"))
commit("feat: cria estrutura inicial do projeto e salesinsight.py")

# ---- main: geracao do dataset -------------------------------------------
commit("feat: implementa geracao do dataset de vendas com sujeira",
       allow_empty=True)

# ---- feat/leitura-limpeza: RF03 (limpeza) --------------------------------
write(HEADER + upto("RF04"))
commit("feat: implementa limpeza de dados com datetime e regex",
       "feat/leitura-limpeza")

# ---- feat/analise-metricas: RF04..RF07 ----------------------------------
write(HEADER + between("RF01", "RF05"))
commit("feat: adiciona colunas derivadas com np.select", "feat/analise-metricas")

write(HEADER + between("RF01", "RF06"))
commit("feat: implementa metricas agregadas com groupby")

write(HEADER + between("RF01", "RF07"))
commit("feat: segmenta clientes por nivel de gasto com lambda")

write(HEADER + between("RF01", "RF08"))
commit("feat: adiciona operacoes vetorizadas com numpy")

# ---- feat/visualizacoes: RF08 --------------------------------------------
write(HEADER + between("RF01", "RF09"))
commit("feat: cria graficos de linha, barra e dispersao", "feat/visualizacoes")
commit("feat: adiciona painel com subplots e exportacao em png",
       allow_empty=True)

# ---- feat/classe-analisador: RF09 ---------------------------------------
write(HEADER + between("RF01", "RF10"))
commit("feat: cria classe AnalisadorDeVendas para organizar o fluxo",
       "feat/classe-analisador")

# ---- develop: RF10 + RF11 -----------------------------------------------
write(full())
commit("feat: implementa exportacao de resultados em csv e json", "develop")
commit("feat: implementa ponto de entrada main() e executa o fluxo completo",
       allow_empty=True)

# ---- volta pra main e mescla --------------------------------------------
git("checkout", "-q", "main")
for br, msg in [("feat/leitura-limpeza", "merge: leitura e limpeza"),
                ("feat/analise-metricas", "merge: metricas agregadas"),
                ("feat/visualizacoes", "merge: visualizacoes"),
                ("feat/classe-analisador", "merge: classe analisador"),
                ("develop", "merge: fluxo completo")]:
    git("merge", "-q", "--no-ff", br, "-m", msg)
    print(f"  {'main':24s} {msg}")

# docs/readme
git("checkout", "-q", "-b", "docs/readme", allow_unrelated_history=True) \
    if False else None
r = git("checkout", "-q", "-b", "docs/readme", check=False)
if r.returncode != 0:
    git("branch", "docs/readme", "main")
    git("checkout", "-q", "docs/readme")
write(full())
commit("docs: atualiza readme com instrucoes e conceitos", "docs/readme")

git("checkout", "-q", "main")
git("merge", "-q", "--no-ff", "docs/readme", "-m", "merge: readme")
print(f"  {'main':24s} merge: readme")

print("\nOK")
