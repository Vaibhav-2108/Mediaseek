-- schema.sql
CREATE TABLE IF NOT EXISTS images (
    image_id SERIAL PRIMARY KEY,
    image_path TEXT NOT NULL,
    category TEXT,
    uploaded_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS captions (
    caption_id SERIAL PRIMARY KEY,
    image_id INT REFERENCES images(image_id) ON DELETE CASCADE,
    caption_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS embeddings (
    embed_id SERIAL PRIMARY KEY,
    ref_id INT NOT NULL,
    ref_type TEXT NOT NULL, -- 'image' or 'caption'
    dim_vector DOUBLE PRECISION[] NOT NULL,
    vector_norm DOUBLE PRECISION NOT NULL
);

CREATE FUNCTION array_dot(a DOUBLE PRECISION[], b DOUBLE PRECISION[])
RETURNS DOUBLE PRECISION AS $$
DECLARE
    s DOUBLE PRECISION := 0;
BEGIN
    FOR i IN 1..array_length(a,1) LOOP
        s := s + a[i]*b[i];
    END LOOP;
    RETURN s;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE FUNCTION cosine_similarity(a DOUBLE PRECISION[], a_norm DOUBLE PRECISION, b DOUBLE PRECISION[], b_norm DOUBLE PRECISION)
RETURNS DOUBLE PRECISION AS $$
BEGIN
    IF a_norm=0 OR b_norm=0 THEN RETURN 0; END IF;
    RETURN array_dot(a,b)/(a_norm*b_norm);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE FUNCTION insert_image_with_embedding(p_path TEXT, p_cat TEXT, p_vec DOUBLE PRECISION[])
RETURNS INT AS $$
DECLARE new_id INT; v_norm DOUBLE PRECISION;
BEGIN
    INSERT INTO images(image_path, category) VALUES(p_path, p_cat) RETURNING image_id INTO new_id;
    SELECT sqrt(sum(x*x)) INTO v_norm FROM unnest(p_vec) x;
    INSERT INTO embeddings(ref_id, ref_type, dim_vector, vector_norm) VALUES(new_id,'image',p_vec,v_norm);
    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION insert_caption_with_embedding(p_img INT, p_cap TEXT, p_vec DOUBLE PRECISION[])
RETURNS INT AS $$
DECLARE new_id INT; v_norm DOUBLE PRECISION;
BEGIN
    INSERT INTO captions(image_id, caption_text) VALUES(p_img,p_cap) RETURNING caption_id INTO new_id;
    SELECT sqrt(sum(x*x)) INTO v_norm FROM unnest(p_vec) x;
    INSERT INTO embeddings(ref_id, ref_type, dim_vector, vector_norm) VALUES(new_id,'caption',p_vec,v_norm);
    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION search_similar_images(qv DOUBLE PRECISION[], qn DOUBLE PRECISION, top_k INT DEFAULT 10)
RETURNS TABLE(image_id INT, image_path TEXT, score DOUBLE PRECISION) AS $$
BEGIN
    RETURN QUERY
    SELECT i.image_id, i.image_path, cosine_similarity(e.dim_vector,e.vector_norm,qv,qn)
    FROM embeddings e JOIN images i ON e.ref_id=i.image_id
    WHERE e.ref_type='image'
    ORDER BY cosine_similarity(e.dim_vector,e.vector_norm,qv,qn) DESC
    LIMIT top_k;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION search_similar_captions(qv DOUBLE PRECISION[], qn DOUBLE PRECISION, top_k INT DEFAULT 10)
RETURNS TABLE(caption_id INT, caption_text TEXT, image_id INT, image_path TEXT, score DOUBLE PRECISION) AS $$
BEGIN
    RETURN QUERY
    SELECT c.caption_id, c.caption_text, i.image_id, i.image_path,
           cosine_similarity(e.dim_vector,e.vector_norm,qv,qn)
    FROM embeddings e
    JOIN captions c ON e.ref_id=c.caption_id
    JOIN images i ON i.image_id=c.image_id
    WHERE e.ref_type='caption'
    ORDER BY cosine_similarity(e.dim_vector,e.vector_norm,qv,qn) DESC
    LIMIT top_k;
END;
$$ LANGUAGE plpgsql;
