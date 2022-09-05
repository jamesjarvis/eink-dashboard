//! An example generating julia fractals I think.

use std::process::Command;

use reqwest::Client;

fn create_image() {
    let imgx = 800;
    let imgy = 800;

    let scalex = 3.0 / imgx as f32;
    let scaley = 3.0 / imgy as f32;

    // Create a new ImgBuf with width: imgx and height: imgy
    let mut imgbuf = image::ImageBuffer::new(imgx, imgy);

    // Iterate over the coordinates and pixels of the image
    for (x, y, pixel) in imgbuf.enumerate_pixels_mut() {
        let r = (0.3 * x as f32) as u8;
        let b = (0.3 * y as f32) as u8;
        *pixel = image::Rgb([r, 0, b]);
    }

    // A redundant loop to demonstrate reading image data
    for x in 0..imgx {
        for y in 0..imgy {
            let cx = y as f32 * scalex - 1.5;
            let cy = x as f32 * scaley - 1.5;

            let c = num_complex::Complex::new(-0.4, 0.6);
            let mut z = num_complex::Complex::new(cx, cy);

            let mut i = 0;
            while i < 255 && z.norm() <= 2.0 {
                z = z * z + c;
                i += 1;
            }

            let pixel = imgbuf.get_pixel_mut(x, y);
            let image::Rgb(data) = *pixel;
            *pixel = image::Rgb([data[0], i as u8, data[2]]);
        }
    }

    // Save the image as “fractal.png”, the format is deduced from the path
    imgbuf.save("fractal.png").unwrap();

    Command::new("open")
            .arg("fractal.png")
            .output()
            .expect("failed to execute process");
}


async fn make_requests(client: Client) -> Result<String, reqwest::Error>{
    const URL_DAD_JOKE: &str = "https://icanhazdadjoke.com/";

    let dad_joke = client.get(URL_DAD_JOKE)
        .header("Accept", "text/plain")
        .send();

    let dad_joke_2 = client.get(URL_DAD_JOKE)
        .header("Accept", "text/plain")
        .send();

    let reqs = futures::join!(dad_joke, dad_joke_2);
    let dad_joke_resp = reqs.0?.text().await?;
    let dad_joke_resp_2 = reqs.1?.text().await?;

    let mut resp = dad_joke_resp.to_owned();
    resp.push_str("\n");
    resp.push_str(&dad_joke_resp_2);

    return Ok(resp)
}


#[tokio::main]
async fn main() {
    // Testing image creation.
    // create_image();

    // Testing request making.
    let client = Client::new();

    let output = make_requests(client);

    let output = futures::executor::block_on(output);

    eprintln!("{}", output.unwrap())
}