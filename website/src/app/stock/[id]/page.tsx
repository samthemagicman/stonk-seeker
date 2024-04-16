import { Badge } from "~/app/_components/ui/badge";
import Main from "~/app/_components/ui/main";
import { getStockComments, getStockMentionsOverTime } from "~/server/db";

export default async function Page({ params }: { params: { id: string } }) {
  const comments = await getStockComments(params.id);
  const stockMentionsTimeline = await getStockMentionsOverTime(params.id);
  const commentsArray = Object.values(comments);
  return (
    <Main>
      <h1 className="text-center text-2xl font-bold">
        {params.id.toUpperCase()}
      </h1>

      <h2 className="text-center text-lg">Comments</h2>
      <ul className="flex flex-col gap-5">
        {commentsArray.map((comment) => (
          <li key={comment.comment} className="rounded-lg border p-4 shadow-sm">
            <p>{comment.comment}</p>
            <div className="pt-3">
              <ul>
                {comment.mentions.map((mention) => (
                  <li className="inline-block pb-2 pr-2" key={mention}>
                    <Badge>{mention}</Badge>
                  </li>
                ))}
              </ul>
            </div>
          </li>
        ))}
      </ul>
    </Main>
  );
}
