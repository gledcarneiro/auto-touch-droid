"""
🧪 TESTE DO SISTEMA INTEGRADO - LOCAL + GITHUB
"""

from memory_system import ClaudeMemorySystem

def test_integrated_system():
    """Testa o sistema de memória integrado com GitHub"""
    print("🧪 TESTANDO SISTEMA INTEGRADO")
    print("=" * 50)
    
    # Inicializar sistema com GitHub
    memory = ClaudeMemorySystem(enable_github=True)
    
    # Testar salvamento (deve sincronizar automaticamente)
    print("\n📝 Testando salvamento com sincronização automática...")
    interaction_id = memory.save_universal_interaction(
        "Teste do sistema integrado GitHub + Local",
        "teste_integracao"
    )
    print(f"✅ Interação salva: {interaction_id}")
    
    # Mostrar status
    print("\n📊 Status da parceria:")
    status = memory.get_partnership_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Testar sincronização manual
    print("\n🔄 Testando sincronização manual...")
    success = memory.sync_to_github_now()
    
    if success:
        print("🎉 SISTEMA INTEGRADO FUNCIONANDO PERFEITAMENTE!")
        print("🌐 Memória local + GitHub sincronizada!")
        print("🚀 Pronto para acesso universal de qualquer IA!")
    else:
        print("⚠️ Problema na sincronização")
    
    return success

if __name__ == "__main__":
    test_integrated_system()