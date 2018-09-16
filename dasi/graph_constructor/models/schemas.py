from marshmallow import Schema, fields


class ContextSchema(Schema):
    circular = fields.Boolean()
    length = fields.Int()
    start = fields.Int()
    name = fields.String()
    id = fields.String()


class RegionSchema(Schema):
    id = fields.String()
    start = fields.Int()
    end = fields.Int()
    direction = fields.Int()
    # direction = fields.Method(serialize="get_strand", deserialize="load_strand", data_key="strand")
    context = fields.Nested(ContextSchema)
    length = fields.Int()


class ContigSchema(Schema):
    query = fields.Nested(RegionSchema)
    subject = fields.Nested(RegionSchema)
    quality = fields.Int(missing=1)
    metadata = fields.Dict()
    alignment_length = fields.Int()
    name = fields.Str()
    contig_id = fields.Str()
    contig_type = fields.Str()


class ContigContainerSchema(Schema):
    contigs = fields.Nested(ContigSchema, many=True)

# return ContigRegion(
#     result["q_start"],
#     result["q_end"],
#     Context(result['query_length'], result['query_circular'], BlastContig.START_INDEX),
#     name=result["query_acc"],
#     forward=True,
#     sequence=result["query_seq"],
#     filename=result['query_filename'],
# )