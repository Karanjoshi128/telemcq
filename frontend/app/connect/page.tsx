import { redirect } from "next/navigation";
import { Nav } from "@/components/nav";
import { supabaseServer } from "@/lib/supabase/server";
import { ConnectClient } from "./client";

export default async function ConnectPage() {
  const sb = await supabaseServer();
  const { data } = await sb.auth.getUser();
  if (!data.user) redirect("/login");
  return (
    <>
      <Nav email={data.user.email} />
      <main className="mx-auto max-w-xl px-4 py-6 sm:py-10">
        <ConnectClient />
      </main>
    </>
  );
}
