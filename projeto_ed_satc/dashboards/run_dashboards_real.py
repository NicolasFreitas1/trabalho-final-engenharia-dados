# -*- coding: utf-8 -*-
"""
Script para executar os dashboards com dados reais do medalhão Gold
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    """Função principal para executar os dashboards"""
    
    # Obter o diretório atual
    current_dir = Path(__file__).parent
    
    print("🚀 Iniciando Dashboards com Dados Reais do Medalhão Gold")
    print("=" * 60)
    
    # Verificar se os arquivos existem
    dashboard_tabelas = current_dir / "dashboard_tabelas_real.py"
    dashboard_kpis = current_dir / "dashboard_kpis_real.py"
    
    if not dashboard_tabelas.exists():
        print(f"❌ Erro: Arquivo {dashboard_tabelas} não encontrado!")
        return
    
    if not dashboard_kpis.exists():
        print(f"❌ Erro: Arquivo {dashboard_kpis} não encontrado!")
        return
    
    print("📊 Dashboards disponíveis:")
    print("1. Dashboard de Tabelas (dados reais)")
    print("2. Dashboard de KPIs e Métricas (dados reais)")
    print("3. Executar ambos")
    
    try:
        escolha = input("\nEscolha uma opção (1, 2 ou 3): ").strip()
        
        if escolha == "1":
            print("\n🎯 Executando Dashboard de Tabelas com dados reais...")
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                str(dashboard_tabelas),
                "--server.port", "8501",
                "--server.headless", "true"
            ])
            
        elif escolha == "2":
            print("\n📈 Executando Dashboard de KPIs com dados reais...")
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                str(dashboard_kpis),
                "--server.port", "8502",
                "--server.headless", "true"
            ])
            
        elif escolha == "3":
            print("\n🔄 Executando ambos os dashboards...")
            print("📊 Dashboard de Tabelas: http://localhost:8501")
            print("📈 Dashboard de KPIs: http://localhost:8502")
            
            # Executar em paralelo
            processo1 = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", 
                str(dashboard_tabelas),
                "--server.port", "8501"
            ])
            
            processo2 = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", 
                str(dashboard_kpis),
                "--server.port", "8502"
            ])
            
            try:
                print("\n✅ Dashboards iniciados com sucesso!")
                print("Pressione Ctrl+C para parar os dashboards...")
                processo1.wait()
                processo2.wait()
            except KeyboardInterrupt:
                print("\n🛑 Parando dashboards...")
                processo1.terminate()
                processo2.terminate()
                processo1.wait()
                processo2.wait()
                print("✅ Dashboards parados com sucesso!")
                
        else:
            print("❌ Opção inválida!")
            return
            
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário!")
    except Exception as e:
        print(f"❌ Erro ao executar dashboards: {e}")

if __name__ == "__main__":
    main() 