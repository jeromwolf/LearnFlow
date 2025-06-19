console.log('Debug test is running');

test('debug test', () => {
  console.log('Inside test');
  expect(true).toBe(true);
});
