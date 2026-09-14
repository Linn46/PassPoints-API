const delaunayLayer =
    document.getElementById("delaunay-layer");


function clearDelaunay() {

    delaunayLayer.innerHTML = "";
}


function drawDelaunay(points) {

    clearDelaunay();


    if (!points || points.length < 3) {
        return;
    }


    const image =
        document.getElementById("selected-image");

    const imageArea =
        document.getElementById("image-area");


    const imageRect =
        image.getBoundingClientRect();

    const areaRect =
        imageArea.getBoundingClientRect();


    delaunayLayer.setAttribute(
        "width",
        areaRect.width
    );

    delaunayLayer.setAttribute(
        "height",
        areaRect.height
    );


    const imageData =
        getImageData();


    if (!imageData) {
        return;
    }


    const visualPoints =
        points.map((point) => {

            const x =
                imageRect.left -
                areaRect.left +
                (point.x / imageData.width) *
                imageRect.width;

            const y =
                imageRect.top -
                areaRect.top +
                (point.y / imageData.height) *
                imageRect.height;

            return {
                x,
                y,
            };
        });


    const triangles =
        calculateDelaunayTriangles(
            visualPoints
        );


    triangles.forEach((triangle) => {

        const p1 =
            visualPoints[triangle[0]];

        const p2 =
            visualPoints[triangle[1]];

        const p3 =
            visualPoints[triangle[2]];


        const polygon =
            document.createElementNS(
                "http://www.w3.org/2000/svg",
                "polygon"
            );


        polygon.setAttribute(
            "points",
            `${p1.x},${p1.y} ${p2.x},${p2.y} ${p3.x},${p3.y}`
        );


        polygon.classList.add(
            "delaunay-triangle"
        );


        delaunayLayer.appendChild(
            polygon
        );
    });
}


function calculateDelaunayTriangles(points) {

    if (points.length < 3) {
        return [];
    }


    const triangles = [];


    for (let i = 0; i < points.length - 2; i++) {

        for (let j = i + 1; j < points.length - 1; j++) {

            for (let k = j + 1; k < points.length; k++) {

                if (
                    isDelaunayTriangle(
                        points,
                        i,
                        j,
                        k
                    )
                ) {
                    triangles.push([
                        i,
                        j,
                        k,
                    ]);
                }
            }
        }
    }


    return removeDuplicateTriangles(
        triangles
    );
}


function isDelaunayTriangle(
    points,
    i,
    j,
    k
) {

    const a = points[i];
    const b = points[j];
    const c = points[k];


    const determinant =
        2 *
        (
            a.x * (b.y - c.y) +
            b.x * (c.y - a.y) +
            c.x * (a.y - b.y)
        );


    if (Math.abs(determinant) < 0.000001) {
        return false;
    }


    const d =
        (
            a.x ** 2 +
            a.y ** 2
        ) * (b.y - c.y) +

        (
            b.x ** 2 +
            b.y ** 2
        ) * (c.y - a.y) +

        (
            c.x ** 2 +
            c.y ** 2
        ) * (a.y - b.y);


    const ux = d / determinant;


    const e =
        (
            a.x ** 2 +
            a.y ** 2
        ) * (c.x - b.x) +

        (
            b.x ** 2 +
            b.y ** 2
        ) * (a.x - c.x) +

        (
            c.x ** 2 +
            c.y ** 2
        ) * (b.x - a.x);


    const uy = e / determinant;


    const radiusSquared =
        (ux - a.x) ** 2 +
        (uy - a.y) ** 2;


    const tolerance = 0.000001;


    for (let index = 0; index < points.length; index++) {

        if (
            index === i ||
            index === j ||
            index === k
        ) {
            continue;
        }


        const point =
            points[index];


        const distanceSquared =
            (point.x - ux) ** 2 +
            (point.y - uy) ** 2;


        if (
            distanceSquared <
            radiusSquared - tolerance
        ) {
            return false;
        }
    }


    return true;
}


function removeDuplicateTriangles(
    triangles
) {

    const unique =
        new Set();

    const result = [];


    triangles.forEach((triangle) => {

        const key =
            [...triangle]
                .sort((a, b) => a - b)
                .join("-");


        if (!unique.has(key)) {

            unique.add(key);

            result.push(triangle);
        }
    });


    return result;
}