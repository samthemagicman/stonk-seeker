-- Might be worth changing to MATERIALIZED VIEW for performance
CREATE VIEW top_stock_mentions AS
    SELECT symbol, COUNT(*) as mentions
    FROM public.stock_mentions
    WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '1 day'
    GROUP BY symbol
    ORDER BY mentions DESC, latest_mention DESC
    LIMIT 10;

CREATE OR REPLACE FUNCTION get_comments_for_symbol(symbol_name text)
RETURNS TABLE(body text, created_at timestamp with time zone) AS $$
BEGIN
    RETURN QUERY 
    SELECT comments.body, comments.created_at
    FROM public.stock_mentions AS stock_mentions
    JOIN public.comments AS comments ON stock_mentions.comment_id = comments.id
    WHERE stock_mentions.symbol = symbol_name
    ORDER BY comments.created_at DESC
    LIMIT 20;
END; $$
LANGUAGE plpgsql;

DROP FUNCTION get_mentions_by_symbol(symbol_param text);
CREATE OR REPLACE FUNCTION get_mentions_by_symbol(symbol_param TEXT)
RETURNS TABLE (
    time_interval TIMESTAMPTZ,
    symbol CHARACTER VARYING(5),
    mentions BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        date_trunc('hour', created_at) + 
            (((date_part('minute', created_at)::integer / 10) * 10) || ' minutes')::interval AS time_interval,
        sm.symbol,
        count(*) AS mentions
    FROM 
        stock_mentions sm
    WHERE 
        sm.created_at > (CURRENT_TIMESTAMP - interval '1 day')
        AND sm.symbol = symbol_param
    GROUP BY 
        date_trunc('hour', sm.created_at) + 
            (((date_part('minute', sm.created_at)::integer / 10) * 10) || ' minutes')::interval,
        sm.symbol
    ORDER BY 
        time_interval ASC, 
        count(*) DESC;
END;
$$ LANGUAGE plpgsql;
