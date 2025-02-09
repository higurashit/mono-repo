import 'dart:math' as math;

var rand = math.Random();

double randomInRange(double min, double max) {
  return min + rand.nextDouble() * (max - min);
}

int randomIntInRange(int min, int max) {
  return min + rand.nextInt(max - min + 1);
}

int randomIntInArray(List<int> arr) {
  return arr[rand.nextInt(arr.length)];
}

int randomPlusOrMinus() {
  return randomIntInArray([1, -1]);
}
