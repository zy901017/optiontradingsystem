import json
from option_strategy_system import OptionStrategySystem


def handler(event, context):
    """
    Vercel serverless function entry point.

    This function expects query parameters `symbol` and `objective`.
    It instantiates the OptionStrategySystem and returns the top
    candidate strategy as JSON.

    Parameters
    ----------
    event : dict
        AWS lambda/Vercel style event object containing `queryStringParameters`.
    context : dict
        Context object (unused).

    Returns
    -------
    dict
        HTTP response with status code and JSON body.
    """
    # Extract query parameters
    params = event.get('queryStringParameters') or {}
    symbol = params.get('symbol', 'AAPL')
    objective = params.get('objective', 'income')

    system = OptionStrategySystem()
    best = system.get_best_strategy(symbol, objective)

    # Convert StrategyCandidate to serialisable dict
    if best:
        candidate = best['candidate']
        response_body = {
            'strategy': candidate.name,
            'legs': candidate.legs,
            'objective': candidate.objective,
            'notes': candidate.notes,
            'score': best['score'],
        }
    else:
        response_body = {'error': 'No strategy found'}

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response_body),
    }