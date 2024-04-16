function Main({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto mb-5 mt-5 flex max-w-7xl flex-col gap-5 px-4 sm:px-6 md:px-8">
      {children}
    </main>
  );
}
export default Main;
