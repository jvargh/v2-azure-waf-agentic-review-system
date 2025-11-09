"""Test the enhanced diagram analyzer output format."""
import asyncio
from backend.app.analysis.document_analyzer import DocumentAnalyzer

async def main():
    analyzer = DocumentAnalyzer()
    
    # Test with comprehensive diagram summary
    summary = """Architecture diagram showing Azure Front Door with WAF, multi-region deployment in East US and West US regions. 
    
Regional components:
- App Service Web Apps (both regions)
- Azure SQL Database with geo-replication
- Redis Cache (distributed)
- Storage Accounts
- Key Vault
- Application Insights

Networking:
- Virtual Networks with front-end and API subnets
- Private Endpoints
- Private DNS zones

Identity: Microsoft Entra ID
Monitoring: Application Insights and Azure Monitor
"""
    
    # Create fake image data with embedded summary as metadata
    fake_image_data = b"fake_diagram_data"
    
    result = await analyzer.analyze_diagram(fake_image_data, 'archdiag-reliable-webapp.jpg', 'image/jpeg')
    
    print("=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    print(result['structured_report']['executive_summary'])
    
    print("\n" + "=" * 80)
    print("ARCHITECTURE OVERVIEW")
    print("=" * 80)
    print(result['structured_report']['architecture_overview'][:1200])
    
    print("\n" + "=" * 80)
    print("CROSS-CUTTING CONCERNS")
    print("=" * 80)
    for dim, text in result['structured_report']['cross_cutting_concerns'].items():
        print(f"\n{dim.upper()}:")
        print(text[:300] + "..." if len(text) > 300 else text)
    
    print("\n" + "=" * 80)
    print("DEPLOYMENT SUMMARY")
    print("=" * 80)
    print(result['structured_report']['deployment_summary'][:800])

if __name__ == "__main__":
    asyncio.run(main())
