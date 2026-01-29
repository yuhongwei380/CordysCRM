package cn.cordys.crm.contract.dto.request;

import cn.cordys.common.dto.BasePageRequest;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
public class ContractPageRequest extends BasePageRequest {

    @Schema(description = "客户ID")
    private String customerId;
}
