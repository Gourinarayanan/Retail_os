import asyncio
from agents.ceo_agent import run_full_pipeline

async def main():
    state = await run_full_pipeline()
    print('Briefing Text:')
    print(state['daily_brief'])
    print('\nOrders Draft Reasoning snippet:')
    for order in state['orders_draft'][:2]:
        name = order.get('product_name')
        ai_reasoning = order.get('ai_reasoning')
        print(f"- {name}:\n{ai_reasoning}\n")

asyncio.run(main())
