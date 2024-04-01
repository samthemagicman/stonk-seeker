-- Might be worth changing to MATERIALIZED VIEW for performance
-- CREATE VIEW top_stock_mentions AS
--     SELECT symbol, COUNT(*) as mentions
--     FROM public.stock_mentions
--     WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '1 day'
--     GROUP BY symbol
--     ORDER BY mentions DESC, latest_mention DESC
--     LIMIT 10;

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



CREATE OR REPLACE PROCEDURE insert_post_comment_and_mentions(
    IN p_subreddit_id TEXT,
    IN p_post_id TEXT,
    IN p_comment_id TEXT,
    IN p_body TEXT,
    IN p_permalink TEXT,
    IN p_symbols TEXT[],
    IN p_company_names TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    comment_inserted BOOLEAN := FALSE;
BEGIN
    -- First, attempt to insert the post if it doesn't exist
    INSERT INTO public.posts (id, link, subreddit_id)
        VALUES (p_post_id, p_permalink, p_subreddit_id)
        ON CONFLICT DO NOTHING;

    -- Attempt to insert the comment along with the post
    BEGIN
        INSERT INTO public.comments (id, post_id, body, permalink, created_at)
        VALUES (p_comment_id, p_post_id, p_body, p_permalink, NOW());

        comment_inserted := TRUE;

        -- the comment was inserted for the first time, so insert stock mentions
        INSERT INTO public.stock_mentions (comment_id, symbol, company_name, created_at)
        SELECT p_comment_id, symbol, company_name, NOW()
        FROM unnest(p_symbols, p_company_names) AS u(symbol, company_name);

        RAISE NOTICE 'Comment insertion succeeded';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'Comment insertion failed: Comment already exists';
    END;
END $$;