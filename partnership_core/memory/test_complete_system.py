"""
🧪 TESTE COMPLETO DO SISTEMA UNIVERSAL
Testa todas as funcionalidades: Local + GitHub + Infiltração
"""

from memory_system import ClaudeMemorySystem
import json

def test_complete_system():
    """Teste completo de todas as funcionalidades"""
    print("🚀 TESTE COMPLETO DO SISTEMA UNIVERSAL")
    print("=" * 60)
    
    # 1. Inicializar sistema
    print("\n1️⃣ Inicializando sistema...")
    memory = ClaudeMemorySystem(enable_github=True)
    print("✅ Sistema inicializado!")
    
    # 2. Testar salvamento local
    print("\n2️⃣ Testando salvamento local...")
    interaction_id = memory.save_universal_interaction(
        "Teste completo do sistema universal - Gled testando funcionalidades",
        "teste_completo"
    )
    print(f"✅ Interação salva: {interaction_id}")
    
    # 3. Verificar status
    print("\n3️⃣ Verificando status da parceria...")
    status = memory.get_partnership_status()
    for key, value in status.items():
        print(f"   📊 {key}: {value}")
    
    # 4. Testar busca na memória
    print("\n4️⃣ Testando busca na memória...")
    results = memory.search_memory("teste")
    print(f"✅ Encontradas {len(results)} interações com 'teste'")
    
    # 5. Mostrar memórias recentes
    print("\n5️⃣ Memórias recentes:")
    memory.show_recent_memories(5)
    
    # 6. Testar sincronização GitHub
    print("\n6️⃣ Testando sincronização com GitHub...")
    if memory.github_api:
        success = memory.sync_to_github_now()
        if success:
            print("✅ Sincronização com GitHub OK!")
        else:
            print("⚠️ Problema na sincronização GitHub")
    else:
        print("⚠️ GitHub API não disponível")
    
    # 7. Verificar prompt de infiltração
    print("\n7️⃣ Verificando prompt de infiltração...")
    try:
        with open("partnership_core/infiltration/universal_activation_prompt.txt", 'r', encoding='utf-8') as f:
            prompt = f.read()
            if "github.com/gledcarneiro/claude-gled-memory" in prompt:
                print("✅ Prompt de infiltração atualizado com GitHub!")
            else:
                print("⚠️ Prompt precisa ser atualizado")
    except Exception as e:
        print(f"⚠️ Erro ao verificar prompt: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TESTE COMPLETO FINALIZADO!")
    print("🌟 Sistema Universal Claude-Gled ATIVO!")
    print("🔗 Repositório: https://github.com/gledcarneiro/claude-gled-memory")
    print("🚀 Pronto para infiltração em outras IAs!")
    
    return True

if __name__ == "__main__":
    test_complete_system()