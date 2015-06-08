jsPlumb.Connectors.ExampleConnector = function() {

	jsPlumb.Connectors.Straight.apply(this);
	var self = this;
	    
    var arrowType1 = function(params) {
    	params = params || {};
    	var length = params.length || 20;
    	var width = params.width || 20;
    	var fillStyle = params.fillStyle || "black";
    	var strokeStyle = params.strokeStyle || "yellow";
    	var lineWidth = params.lineWidth || 1;
    	this.draw = function(connector, location, ctx) {    		
			// this is the arrow head position
			var hxy = connector.pointAlongPathFrom(location, length / 2), hx = hxy[0], hy = hxy[1];
			// this is the center of the tail
			var txy = connector.pointAlongPathFrom(location, -length / 2), tx = txy[0], ty = txy[1];
			// this is the tail vector
			var tail = connector.perpendicularToPath(tx, ty, width);
			
			ctx.lineWidth = lineWidth;
			ctx.beginPath();
			ctx.moveTo(hx, hy);
			ctx.lineTo(tail[0][0], tail[0][1]);
			ctx.lineTo(tail[1][0], tail[1][1]);
			ctx.lineTo(hx, hy);
			ctx.closePath();

			if (strokeStyle) {
				ctx.strokeStyle = strokeStyle;
				ctx.stroke();
			}
			
			ctx.fillStyle = fillStyle;
			ctx.fill();
    	};
    };
    
    /**
     * an arrow that folds back on itself instead of having a straight back edge. by default the foldback point is 62.3% along the length of the
     * arrow, which is roughly a golden ratio along the arrow and therefore looks quite nice. you can change that by setting the 'foldback' 
     * parameter when you construct this.  available params are:
     * 
     * length - length in pixels of the arrow
     * width - width in pixels of the arrow's tail at its widest point
     * foldback - a decimal value indicating where along the arrow the tail points should fold back in to.
     */
    var arrowType2 = function(params) {        	
    	params = params || {};
    	var length = params.length || 20;
    	var width = params.width || 20;
    	var fillStyle = params.fillStyle || "black";
    	var strokeStyle = params.strokeStyle || "yellow";
    	var lineWidth = params.lineWidth || 1;
    	// how far along the arrow the lines folding back in come to. default is 62.3%. 
    	var foldback = params.foldback || 0.623;
    	var _getFoldBackPoint = function(connector, location) {
    		if (foldback == 0.5) return connector.pointOnPath(location);
    		else {
    			var adj = 0.5 - foldback; // we calculate relative to the center
    			return connector.pointAlongPathFrom(location, length * adj);        			
    		}
    	};
    	
    	this.draw = function(connector, location, ctx) {
			// this is the arrow head position
			var hxy = connector.pointAlongPathFrom(location, length / 2);
			// this is the center of the tail
			var txy = connector.pointAlongPathFrom(location, -length / 2), tx = txy[0], ty = txy[1];
			// this is the tail vector
			var tail = connector.perpendicularToPath(tx, ty, width);
			// this is the point the tail goes in to
			var cxy = _getFoldBackPoint(connector, location);
			
			ctx.lineWidth = lineWidth;
			ctx.beginPath();
			ctx.moveTo(hxy[0], hxy[1]);
			ctx.lineTo(tail[0][0], tail[0][1]);
			ctx.lineTo(cxy[0], cxy[1]);
			ctx.lineTo(tail[1][0], tail[1][1]);
			ctx.lineTo(hxy[0], hxy[1]);
			ctx.closePath();
			
			if (strokeStyle) {
				ctx.strokeStyle = strokeStyle;
				ctx.stroke();
			}
			ctx.fillStyle = fillStyle;			
			ctx.fill();
    	}
    };

    var _p = self.paint;
    this.paint = function(dimensions, ctx)
    {
    	_p(dimensions,ctx);
        
    	new arrowType1().draw(self, 0.333333333333333, ctx);
    	new arrowType2().draw(self, 0.666666666666666, ctx);
                    
    };
};