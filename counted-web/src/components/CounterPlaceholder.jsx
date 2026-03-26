export default function CounterPlaceholder({ count = 12000 }) {
  return (
    <p className="text-gray-500 text-sm text-center">
      Over {count.toLocaleString()} people have taken action
    </p>
  );
}
