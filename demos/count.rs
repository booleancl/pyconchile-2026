use std::env;
fn main() {
    let limit: u64 = env::args()
        .nth(1).unwrap()
        .parse().unwrap();
    let mut count = 0;
    for number in 1..=limit {
        if number % 7 == 0 {
            count += 1;
        }
    }
    println!("{count}");
}
