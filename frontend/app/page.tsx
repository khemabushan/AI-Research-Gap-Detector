import { SearchHero } from "@/components/home/search-hero";
import { HowItWorks } from "@/components/home/how-it-works";

export default function HomePage() {
  return (
    <div className="container flex flex-col gap-20 py-20 sm:py-28">
      <SearchHero />
      <div className="mx-auto w-full max-w-3xl">
        <HowItWorks />
      </div>
    </div>
  );
}
