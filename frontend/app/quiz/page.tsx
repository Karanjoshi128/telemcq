import { redirect } from "next/navigation";
import { Nav } from "@/components/nav";
import { supabaseServer } from "@/lib/supabase/server";
import { QuizClient } from "./client";

export default async function QuizPage() {
  const sb = await supabaseServer();
  const { data } = await sb.auth.getUser();
  if (!data.user) redirect("/login");
  return (
    <>
      <Nav email={data.user.email} />
      <main className="mx-auto max-w-3xl px-4 py-6 sm:py-10">
        <QuizClient />
      </main>
    </>
  );
}
