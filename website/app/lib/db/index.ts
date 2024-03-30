import pg from 'pg'

export const pool = new pg.Pool({
    host: process.env.POSTGRES_HOST,
    user: process.env.POSTGRES_USER,
    password: process.env.POSTGRES_PASSWORD,
    database: process.env.POSTGRES_DATABASE,
    port: parseInt(process.env.POSTGRES_PORT ?? "5432"),
    ssl: process.env.NODE_ENV === "production",
})


// export const query = (text: string, params: never) => {
//     return pool.query(text, params)
// }