(function () {
    var fill, h, svg, tooltip, w, xpadding;


    var svg = d3.select("#d3_contig_viewer")
        .select('svg'),
        w = svg.attr('width');
        h = svg.attr('height');

    var xpadding = 50.0;

    tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip");

    d3.json('contigs.json', function (data) {
        console.log(data);
        console.log(data.contigs[0].query.start);
        var query_context_len, xScale, yScale;
        var query = data.contigs[0].query;

        query_context_len = query.context.length;

        xScale = d3.scaleLinear().domain([0, query_context_len]).range([0 + xpadding, w - xpadding]);

        // fill in top query rectangle
        var top_bar_width = query.context.length;
        var top_bar_height = 10;
        var top_bar_y = 20;
        var top_bar_opacity = 0.5;
        if (query.context.circular) {
            top_bar_width = query_context_len / 2.0;
        }

        svg.append('rect')
            .attr('x', xScale(0))
            .attr('width', xScale(top_bar_width) - xScale(0))
            .attr('y', top_bar_y - top_bar_height).attr('height', top_bar_height)
            .attr('opacity', top_bar_opacity)
            .attr('fill', 'blue');

        // in circular fill in next query rectangle
        if (query.context.circular) {
            svg.append('rect')
                .attr('x', xScale(top_bar_width))
                .attr('width', xScale(top_bar_width) - xScale(0))
                .attr('y', top_bar_y - top_bar_height).attr('height', top_bar_height)
                .attr('opacity', top_bar_opacity)
                .attr('fill', 'purple');
        }

        // xAxis
        var xAxis = d3.axisBottom(xScale);  // apply axis
        var xAxisGroup = svg.append('g')
            .attr('transform', 'translate(0,' + top_bar_y + ')')
            .call(xAxis);

        // midpoint
        svg.append('rect')
            .attr('x', xScale(query_context_len / 2.0))
            .attr('width', 3)
            .attr('y', top_bar_y).attr('height', 20)
            .attr('fill', 'black');

        // contig boxes

        var contig_height = 4;
        var contig_padding = 2;
        var contig_area_y = top_bar_y + 20;
        var contig_area_height = (contig_height + contig_padding) * data.contigs.length;
        svg.attr('height', contig_area_height+100);  // re-adjust svg height

        yScale = d3.scaleLinear().domain([0, data.contigs.length]).range([contig_area_y, contig_area_height]);
        svg.selectAll('rects')
            .data(data.contigs)
            .enter()
            .append('rect')
            .attr('x', function (d) {
                return xScale(d.query.start);
            }).attr('y', function (d, i) {
            return yScale(i)
        })
            .style('fill', contig_fill)
            .attr('width', function (d) {
                return xScale(d.query.end) - xScale(d.query.start);
            }).attr('height', contig_height).attr('fill', fill).attr('opacity', 0.9).on("mouseover", function (d) {
                var coordinates;
                coordinates = d3.mouse(this);
                d3.select(this).style("fill", 'red');
                return tooltip.text(d.query.name + ' (' + d.query.start + '-' + d.query.end + ') ' + d.contig_type + ' ' + d.contig_id + ' ' + d.alignment_length).style("visibility", "visible");
            }).on("mousemove", function () {
                return tooltip.style("top", (d3.event.pageY - 10) + "px").style("left", (d3.event.pageX + 10) + "px");
            }).on("mouseout", function (d) {
                d3.select(this).style('fill', contig_fill);
                return tooltip.style("visibility", "hidden");
            });

        // vertical lines
        svg.selectAll('rects').data(data.contigs).enter().append('rect').attr('x', function (d) {
            return xScale(d.query.start);
        }).attr('y', top_bar_y)
            .attr('width', 1).attr('height', h).attr('fill', 'black').attr('opacity', 0.1);
        svg.selectAll('rects').data(data.contigs).enter().append('rect').attr('x', function (d) {
            return xScale(d.query.end);
        }).attr('y', top_bar_y)
            .attr('width', 1).attr('height', h).attr('fill', 'blue').attr('opacity', 0.1);
        // return d3.json('primer_data.json', function (primerdata) {
        //     return svg.selectAll('primer_rects').data(primerdata.contigs).enter().append('rect').attr('x', function (d) {
        //         return xScale(d.query.start);
        //     }).attr('y', function (d, i) {
        //         return 100;
        //     }).attr('width', 1).attr('height', h).attr('fill', "red").attr('opacity', 0.35);
        // });
    });

    contig_fill = function (d) {
        if (d.contig_type === 'contig') {
            return 'black';
        }
        if (d.contig_type === 'circular_partition') {
            return 'purple';
        }
        if (d.contig_type === 'gap') {
            return 'blue';
        }
        return 'orange';
    };

}).call(this);

//# sourceMappingURL=baseviewer.js.map