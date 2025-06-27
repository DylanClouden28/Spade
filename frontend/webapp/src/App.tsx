import { createSignal } from "solid-js";

function App() {
  const [count, setCount] = createSignal(0);

  return (
    <div class="relative">
      <div class="absolute justify-center items-center text-blue-400">
        <div>Hello test 123!</div>
      </div>
    </div>
  );
}

export default App;
